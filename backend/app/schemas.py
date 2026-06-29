from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class UserType(str, Enum):
    FOUNDATION = "foundation"
    NORMAL = "normal"

class CertificateStatus(str, Enum):
    DRAFT = "draft"
    ISSUED = "issued"
    EXPIRED = "expired"
    REVOKED = "revoked"

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)
    company_name: Optional[str] = None
    user_type: UserType = UserType.NORMAL

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    is_verified: bool
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Template Schemas
class TemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    template_json: Dict[str, Any]
    is_default: bool = False
    is_public: bool = False

class TemplateCreate(TemplateBase):
    pass

class TemplateResponse(TemplateBase):
    id: int
    thumbnail: Optional[str]
    created_by: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Certificate Schemas
class CertificateBase(BaseModel):
    recipient_name: str = Field(..., min_length=1, max_length=100)
    recipient_email: EmailStr
    recipient_company: Optional[str] = None
    certificate_title: str = Field(..., min_length=1, max_length=200)
    certificate_description: Optional[str] = None
    expiry_date: Optional[datetime] = None
    template_id: int = 1

class CertificateCreate(CertificateBase):
    send_email: bool = False

class CertificateResponse(CertificateBase):
    id: int
    certificate_id: str
    issue_date: datetime
    status: CertificateStatus
    verification_hash: Optional[str]
    verification_url: Optional[str]
    viewed_count: int
    downloaded_count: int
    created_by: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Verification Schemas
class VerificationResponse(BaseModel):
    valid: bool
    certificate_id: Optional[str] = None
    recipient_name: Optional[str] = None
    recipient_email: Optional[str] = None
    certificate_title: Optional[str] = None
    issue_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    status: Optional[str] = None
    verification_count: Optional[int] = None
    is_blockchain_verified: bool = False
    message: str = ""

# Bulk Upload Schemas
class BulkUploadResponse(BaseModel):
    total: int
    successful: int
    failed: int
    errors: List[Dict[str, Any]] = []
