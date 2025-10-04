from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class MagicLinkRequest(BaseModel):
    email: EmailStr

class MagicLinkResponse(BaseModel):
    success: bool
    message: str

class AuthCallbackRequest(BaseModel):
    code: str
    state: Optional[str] = None

class AuthResponse(BaseModel):
    success: bool
    access_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: Optional[int] = None
    user: Optional[dict] = None
    message: Optional[str] = None

class SessionLoginRequest(BaseModel):
    access_token: str

class AdminUser(BaseModel):
    id: str
    email: EmailStr
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool = True

class AuditLog(BaseModel):
    id: str
    admin_email: EmailStr
    action: str
    ip_address: str
    user_agent: str
    details: dict
    timestamp: datetime