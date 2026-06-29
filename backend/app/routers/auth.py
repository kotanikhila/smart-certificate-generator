from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
import os
import shutil
import hashlib
import base64
import logging
from .. import models
from ..database import get_db
from ..config import settings

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()

# Export these functions so they can be imported
def get_password_hash(password: str) -> str:
    salt = "cert_salt_2024"
    combined = salt + password
    hash_bytes = hashlib.sha256(combined.encode()).digest()
    return base64.b64encode(hash_bytes).decode()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return get_password_hash(plain_password) == hashed_password

def create_access_token(data: dict):
    import jwt
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

@router.post("/register")
async def register(
    email: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(...),
    company_name: str = Form(None),
    user_type: str = Form("normal"),
    db: Session = Depends(get_db)
):
    logger.info(f"Registration attempt for email: {email}")
    try:
        # Check if user exists
        existing = db.query(models.User).filter(models.User.email == email).first()
        if existing:
            logger.warning(f"Email already registered: {email}")
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create user
        hashed = get_password_hash(password)
        logger.info(f"Password hashed successfully")
        
        user_type_enum = models.UserType.FOUNDATION if user_type == "foundation" else models.UserType.NORMAL
        
        user = models.User(
            email=email,
            password_hash=hashed,
            full_name=full_name,
            company_name=company_name,
            user_type=user_type_enum,
            is_verified=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"User created successfully: {user.id}")
        
        return {
            "message": "Registration successful", 
            "user_id": user.id, 
            "is_verified": user.is_verified
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    logger.info(f"Login attempt for: {form_data.username}")
    try:
        user = db.query(models.User).filter(models.User.email == form_data.username).first()
        if not user:
            logger.warning(f"User not found: {form_data.username}")
            raise HTTPException(status_code=401, detail="Incorrect email or password")
        
        if not verify_password(form_data.password, user.password_hash):
            logger.warning(f"Invalid password for: {form_data.username}")
            raise HTTPException(status_code=401, detail="Incorrect email or password")
        
        user.last_login = datetime.now()
        db.commit()
        
        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.id}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_type": user.user_type.value,
            "is_verified": user.is_verified,
            "user_id": user.id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/me")
async def get_current_user(
    token: str,
    db: Session = Depends(get_db)
):
    import jwt
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "company_name": user.company_name,
            "user_type": user.user_type.value,
            "is_verified": user.is_verified,
            "created_at": user.created_at
        }
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
