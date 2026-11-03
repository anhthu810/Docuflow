from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=True) # None for Google OAuth
    full_name = Column(String(255), default="")
    credits = Column(Integer, default=20)
    is_active = Column(Boolean, default=True)
    role = Column(String(50), default="user") # 'user', 'admin'
    created_at = Column(DateTime, default=datetime.utcnow)

    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=True)
    format = Column(String(100), default="PDF • 1 trang")
    supplier = Column(String(255), default="")
    tax_id = Column(String(50), default="")
    invoice_no = Column(String(100), default="")
    date = Column(String(50), default="")
    subtotal = Column(Float, default=0.0)
    tax = Column(Float, default=0.0)
    total = Column(Float, default=0.0)
    has_low_confidence = Column(Boolean, default=False)
    audit_done = Column(Boolean, default=True)
    raw_extracted_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="documents")

class ContactMessage(Base):
    __tablename__ = "contact_messages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    topic = Column(String(100), default="")
    message = Column(Text, nullable=False)
    status = Column(String(50), default="new") # 'new', 'replied'
    created_at = Column(DateTime, default=datetime.utcnow)

