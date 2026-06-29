from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, JSON, Float, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base
import enum

class UserType(str, enum.Enum):
    FOUNDATION = "foundation"
    NORMAL = "normal"

class CertificateStatus(str, enum.Enum):
    DRAFT = "draft"
    ISSUED = "issued"
    EXPIRED = "expired"
    REVOKED = "revoked"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    company_name = Column(String)
    user_type = Column(Enum(UserType), default=UserType.NORMAL)
    is_verified = Column(Boolean, default=False)
    verification_document = Column(String)
    verification_notes = Column(Text)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    certificates = relationship("Certificate", back_populates="creator", cascade="all, delete-orphan")
    templates = relationship("CertificateTemplate", back_populates="creator", cascade="all, delete-orphan")

class CertificateTemplate(Base):
    __tablename__ = "certificate_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    template_json = Column(JSON, nullable=False)
    thumbnail = Column(String)
    is_default = Column(Boolean, default=False)
    is_public = Column(Boolean, default=False)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    creator = relationship("User", back_populates="templates")
    certificates = relationship("Certificate", back_populates="template")

class Certificate(Base):
    __tablename__ = "certificates"
    
    id = Column(Integer, primary_key=True, index=True)
    certificate_id = Column(String, unique=True, index=True, nullable=False)
    recipient_name = Column(String, nullable=False)
    recipient_email = Column(String, nullable=False)
    recipient_company = Column(String)
    certificate_title = Column(String, nullable=False)
    certificate_description = Column(Text)
    issue_date = Column(DateTime(timezone=True), nullable=False)
    expiry_date = Column(DateTime(timezone=True))
    created_by = Column(Integer, ForeignKey("users.id"))
    template_id = Column(Integer, ForeignKey("certificate_templates.id"))
    status = Column(Enum(CertificateStatus), default=CertificateStatus.ISSUED)
    
    qr_code_path = Column(String)
    verification_hash = Column(String, unique=True)
    verification_url = Column(String)
    pdf_path = Column(String)
    image_path = Column(String)
    cloudinary_url = Column(String)
    aws_s3_url = Column(String)
    firebase_url = Column(String)
    custom_fields = Column(JSON, default={})
    is_blockchain_verified = Column(Boolean, default=False)
    blockchain_tx_hash = Column(String)
    
    viewed_count = Column(Integer, default=0)
    downloaded_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    creator = relationship("User", back_populates="certificates")
    template = relationship("CertificateTemplate", back_populates="certificates")
    verification_logs = relationship("VerificationLog", back_populates="certificate", cascade="all, delete-orphan")
    email_logs = relationship("EmailLog", back_populates="certificate", cascade="all, delete-orphan")

class VerificationLog(Base):
    __tablename__ = "verification_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    certificate_id = Column(Integer, ForeignKey("certificates.id"))
    verified_by = Column(String)
    verification_method = Column(String)
    verification_status = Column(Boolean, nullable=False)
    user_agent = Column(String)
    ip_address = Column(String)
    location_data = Column(JSON)
    verified_at = Column(DateTime(timezone=True), server_default=func.now())
    
    certificate = relationship("Certificate", back_populates="verification_logs")

class EmailLog(Base):
    __tablename__ = "email_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    certificate_id = Column(Integer, ForeignKey("certificates.id"))
    recipient_email = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    body = Column(Text)
    status = Column(String)
    error_message = Column(Text)
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    
    certificate = relationship("Certificate", back_populates="email_logs")
