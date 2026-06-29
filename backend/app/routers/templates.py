from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, auth
from ..database import get_db

router = APIRouter()

@router.get("/")
async def get_templates(
    db: Session = Depends(get_db)
):
    templates = db.query(models.CertificateTemplate).all()
    return templates

@router.post("/")
async def create_template(
    template: schemas.TemplateCreate,
    current_user: models.User = Depends(auth.require_foundation),
    db: Session = Depends(get_db)
):
    db_template = models.CertificateTemplate(
        name=template.name,
        description=template.description,
        template_json=template.template_json,
        created_by=current_user.id,
        is_default=template.is_default
    )
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template

@router.get("/{template_id}")
async def get_template(
    template_id: int,
    db: Session = Depends(get_db)
):
    template = db.query(models.CertificateTemplate).filter(
        models.CertificateTemplate.id == template_id
    ).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template
