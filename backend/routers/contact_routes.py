from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import ContactMessage
from backend.schemas import ContactCreate, ContactOut

router = APIRouter(prefix="/api/contact", tags=["Contact"])

@router.post("", response_model=ContactOut)
def create_contact_message(payload: ContactCreate, db: Session = Depends(get_db)):
    msg = ContactMessage(
        name=payload.name.strip(),
        email=payload.email.strip().lower(),
        topic=payload.topic.strip() if payload.topic else "Hỗ trợ chung",
        message=payload.message.strip(),
        status="new"
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg

@router.get("", response_model=List[ContactOut])
def get_contact_messages(db: Session = Depends(get_db)):
    return db.query(ContactMessage).order_by(ContactMessage.created_at.desc()).all()

