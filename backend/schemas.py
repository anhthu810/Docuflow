from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

# --- Auth Schemas ---
class UserRegister(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = ""

class UserLogin(BaseModel):
    email: str
    password: str

class GoogleLogin(BaseModel):
    email: str
    name: Optional[str] = "Google User"

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserOut"

class UserOut(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = ""
    credits: int
    role: str

    class Config:
        from_attributes = True

# --- Document Schemas ---
class DocumentCreate(BaseModel):
    file_name: str
    format: Optional[str] = "PDF • 1 trang"
    supplier: Optional[str] = ""
    tax_id: Optional[str] = ""
    invoice_no: Optional[str] = ""
    date: Optional[str] = ""
    subtotal: Optional[float] = 0.0
    tax: Optional[float] = 0.0
    total: Optional[float] = 0.0
    has_low_confidence: Optional[bool] = False
    audit_done: Optional[bool] = True

class DocumentUpdate(BaseModel):
    supplier: Optional[str] = None
    tax_id: Optional[str] = None
    invoice_no: Optional[str] = None
    date: Optional[str] = None
    subtotal: Optional[float] = None
    tax: Optional[float] = None
    total: Optional[float] = None
    audit_done: Optional[bool] = None
    has_low_confidence: Optional[bool] = None

class DocumentOut(BaseModel):
    id: int
    user_id: Optional[int] = None
    file_name: str
    file_path: Optional[str] = None
    format: str
    supplier: str
    tax_id: str
    invoice_no: str
    date: str
    subtotal: float
    tax: float
    total: float
    has_low_confidence: bool
    audit_done: bool
    created_at: datetime

    class Config:
        from_attributes = True

# --- Contact Schemas ---
class ContactCreate(BaseModel):
    name: str
    email: str
    topic: Optional[str] = "Bắt đầu sử dụng"
    message: str

class ContactOut(BaseModel):
    id: int
    name: str
    email: str
    topic: str
    message: str
    created_at: datetime

    class Config:
        from_attributes = True
