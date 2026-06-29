from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import logging

from .database import engine, Base, SessionLocal
from .routers import auth, certificates, templates, users, verification
from . import models

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create tables
Base.metadata.create_all(bind=engine)

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

# Vercel handler
app = app
