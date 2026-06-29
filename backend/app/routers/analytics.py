from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from ..database import get_db
from .. import models, auth

router = APIRouter()

@router.get("/analytics")
async def get_analytics(
    current_user: models.User = Depends(auth.require_admin),
    db: Session = Depends(get_db)
):
    """Get analytics data for dashboard"""
    today = datetime.now().date()
    
    # Total certificates by month (last 12 months)
    monthly_data = []
    for i in range(12):
        month_start = datetime(today.year, today.month - i, 1)
        month_end = datetime(today.year, today.month - i + 1, 1) if i > 0 else datetime(today.year, today.month + 1, 1)
        count = db.query(models.Certificate).filter(
            models.Certificate.created_at >= month_start,
            models.Certificate.created_at < month_end
        ).count()
        monthly_data.append({
            "month": month_start.strftime("%B %Y"),
            "count": count
        })
    
    # User growth
    total_users = db.query(models.User).count()
    verified_users = db.query(models.User).filter(models.User.is_verified == True).count()
    
    # Recent activity
    recent_activity = db.query(models.ActivityLog).order_by(
        models.ActivityLog.created_at.desc()
    ).limit(10).all()
    
    return {
        "monthly_certificates": monthly_data[::-1],
        "total_users": total_users,
        "verified_users": verified_users,
        "recent_activity": recent_activity,
        "total_certificates": db.query(models.Certificate).count(),
        "total_verifications": db.query(models.VerificationLog).count()
    }
