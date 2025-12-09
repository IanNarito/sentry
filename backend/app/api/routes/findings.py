from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime

from backend.app.core.database import get_db
from backend.app.models.finding import Finding

router = APIRouter()

class FindingResponse(BaseModel):
    id: int
    title: str
    severity: str
    description: str | None
    created_at: datetime
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[FindingResponse])
def get_findings(db: Session = Depends(get_db)):
    return db.query(Finding).order_by(Finding.severity.desc()).all()