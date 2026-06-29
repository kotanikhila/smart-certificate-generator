from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, auth
from ..database import get_db

router = APIRouter()

@router.get("/")
async def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(auth.require_foundation),
    db: Session = Depends(get_db)
):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

@router.post("/verify/{user_id}")
async def verify_user(
    user_id: int,
    current_user: models.User = Depends(auth.require_foundation),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_verified = True
    db.commit()
    db.refresh(user)
    return {"message": "User verified successfully"}

@router.get("/stats")
async def get_user_stats(
    current_user: models.User = Depends(auth.require_foundation),
    db: Session = Depends(get_db)
):
    total = db.query(models.User).count()
    verified = db.query(models.User).filter(models.User.is_verified == True).count()
    pending = total - verified
    
    return {
        "total_users": total,
        "verified_users": verified,
        "pending_verification": pending
    }
