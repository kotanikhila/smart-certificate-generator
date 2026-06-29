from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from .. import models, auth
from ..database import get_db
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/")
async def search_certificates(
    query: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Search certificates by ID, recipient name, email, or title"""
    try:
        certificates = db.query(models.Certificate).filter(
            or_(
                models.Certificate.certificate_id.ilike(f"%{query}%"),
                models.Certificate.recipient_name.ilike(f"%{query}%"),
                models.Certificate.recipient_email.ilike(f"%{query}%"),
                models.Certificate.certificate_title.ilike(f"%{query}%")
            ),
            models.Certificate.created_by == current_user.id
        ).limit(limit).all()
        
        return {
            "total": len(certificates),
            "results": certificates,
            "query": query
        }
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
