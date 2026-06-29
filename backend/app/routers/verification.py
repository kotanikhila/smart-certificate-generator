from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from .. import models, auth
from ..database import get_db

router = APIRouter()

@router.get("/{certificate_id}")
async def verify_certificate(
    certificate_id: str,
    db: Session = Depends(get_db)
):
    # Try to find by certificate_id or verification_hash
    certificate = db.query(models.Certificate).filter(
        (models.Certificate.certificate_id == certificate_id) |
        (models.Certificate.verification_hash == certificate_id)
    ).first()
    
    if not certificate:
        return {"valid": False, "message": "Certificate not found"}
    
    if certificate.expiry_date and certificate.expiry_date < datetime.now():
        return {
            "valid": False,
            "message": "Certificate has expired",
            "expiry_date": certificate.expiry_date
        }
    
    # Log verification
    log = models.VerificationLog(
        certificate_id=certificate.id,
        verification_method="url",
        verification_status=True
    )
    db.add(log)
    certificate.viewed_count += 1
    db.commit()
    
    return {
        "valid": True,
        "certificate_id": certificate.certificate_id,
        "recipient_name": certificate.recipient_name,
        "recipient_email": certificate.recipient_email,
        "certificate_title": certificate.certificate_title,
        "issue_date": certificate.issue_date,
        "expiry_date": certificate.expiry_date,
        "status": certificate.status.value,
        "verification_count": certificate.viewed_count,
        "is_blockchain_verified": certificate.is_blockchain_verified
    }
