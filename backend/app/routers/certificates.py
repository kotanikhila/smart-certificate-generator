from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os
import logging
from .. import models
from ..database import get_db
from ..utils.certificate_generator import CertificateGenerator

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/generate")
async def generate_certificate(
    recipient_name: str = Form(...),
    recipient_email: str = Form(...),
    recipient_company: str = Form(""),
    certificate_title: str = Form("Certificate of Achievement"),
    certificate_description: str = Form("In recognition of outstanding achievement"),
    db: Session = Depends(get_db)
):
    """Generate a certificate"""
    logger.info(f"Generating certificate for {recipient_name}")
    try:
        # Get or create default template
        template = db.query(models.CertificateTemplate).filter(
            models.CertificateTemplate.is_default == True
        ).first()
        
        if not template:
            # Create default template
            template = models.CertificateTemplate(
                name="Default Template",
                description="Default certificate template",
                template_json={
                    "background_color": "#FFFFFF",
                    "border_color": "#1a56db",
                    "title_color": "#1a56db",
                    "name_color": "#1a3a8a",
                    "text_color": "#4b5563"
                },
                is_default=True,
                created_by=1
            )
            db.add(template)
            db.commit()
            db.refresh(template)
        
        # Generate certificate
        generator = CertificateGenerator(template.__dict__)
        data = {
            "recipient_name": recipient_name,
            "recipient_email": recipient_email,
            "recipient_company": recipient_company,
            "certificate_title": certificate_title,
            "certificate_description": certificate_description
        }
        result = generator.generate_certificate(data)
        
        # Save to database
        certificate = models.Certificate(
            certificate_id=result["certificate_id"],
            recipient_name=recipient_name,
            recipient_email=recipient_email,
            recipient_company=recipient_company,
            certificate_title=certificate_title,
            certificate_description=certificate_description,
            issue_date=datetime.now(),
            created_by=1,
            template_id=template.id,
            status=models.CertificateStatus.ISSUED,
            verification_hash=result["verification_hash"],
            verification_url=result["verification_url"],
            pdf_path=result["pdf_path"],
            image_path=result["image_path"],
            qr_code_path=result["qr_path"]
        )
        
        db.add(certificate)
        db.commit()
        db.refresh(certificate)
        
        return {
            "message": "Certificate generated successfully",
            "certificate": result,
            "db_id": certificate.id
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Certificate generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def get_certificates(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all certificates"""
    try:
        certificates = db.query(models.Certificate).offset(skip).limit(limit).all()
        return certificates
    except Exception as e:
        logger.error(f"Error fetching certificates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{certificate_id}")
async def get_certificate(
    certificate_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific certificate by ID"""
    try:
        certificate = db.query(models.Certificate).filter(
            models.Certificate.certificate_id == certificate_id
        ).first()
        if not certificate:
            raise HTTPException(status_code=404, detail="Certificate not found")
        return certificate
    except Exception as e:
        logger.error(f"Error fetching certificate: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{certificate_id}")
async def download_certificate(
    certificate_id: str,
    format: str = "pdf",
    db: Session = Depends(get_db)
):
    """Download a certificate"""
    try:
        certificate = db.query(models.Certificate).filter(
            models.Certificate.certificate_id == certificate_id
        ).first()
        if not certificate:
            raise HTTPException(status_code=404, detail="Certificate not found")
        
        certificate.downloaded_count += 1
        db.commit()
        
        if format == "pdf" and certificate.pdf_path and os.path.exists(certificate.pdf_path):
            return FileResponse(certificate.pdf_path, filename=f"{certificate_id}.pdf", media_type="application/pdf")
        elif certificate.image_path and os.path.exists(certificate.image_path):
            return FileResponse(certificate.image_path, filename=f"{certificate_id}.png", media_type="image/png")
        else:
            raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        logger.error(f"Error downloading certificate: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
