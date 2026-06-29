from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import logging

from .database import engine, Base, SessionLocal
from .routers import auth, certificates, templates, users, verification, search
from .config import settings
from . import models

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create tables
Base.metadata.create_all(bind=engine)

# Create default template if none exists
def create_default_template():
    db = SessionLocal()
    try:
        template = db.query(models.CertificateTemplate).filter(
            models.CertificateTemplate.is_default == True
        ).first()
        if not template:
            default_template = models.CertificateTemplate(
                name="Default Certificate Template",
                description="Beautiful certificate template with modern design",
                template_json={
                    "background_color": "#FFFFFF",
                    "border_color": "#1a56db",
                    "title_color": "#1a56db",
                    "name_color": "#1a3a8a",
                    "text_color": "#4b5563",
                    "width": 1400,
                    "height": 1000
                },
                is_default=True,
                is_public=True,
                created_by=1
            )
            db.add(default_template)
            db.commit()
            logger.info("Default template created successfully")
    except Exception as e:
        logger.error(f"Error creating default template: {e}")
    finally:
        db.close()

create_default_template()

app = FastAPI(
    title="Smart Certificate Generator API",
    description="Complete certificate generation and verification system",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(certificates.router, prefix="/api/certificates", tags=["Certificates"])
app.include_router(templates.router, prefix="/api/templates", tags=["Templates"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(verification.router, prefix="/api/verify", tags=["Verification"])
app.include_router(search.router, prefix="/api/search", tags=["Search"])

@app.get("/")
async def root():
    return {
        "message": "Smart Certificate Generator API",
        "version": "1.0.0",
        "status": "active",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}
