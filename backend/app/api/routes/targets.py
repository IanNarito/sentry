from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.app.core.database import get_db
# FIX: Import 'Target' (singular class), not 'targets'
from backend.app.models.target import Target 
from backend.app.schemas.target import TargetCreate, TargetResponse

router = APIRouter()

@router.post("/", response_model=TargetResponse)
def create_target(target: TargetCreate, db: Session = Depends(get_db)):
    # FIX: Use 'Target' class for queries
    existing = db.query(Target).filter(Target.name == target.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Target already exists")
    
    # Create new target
    new_target = Target(
        name=target.name,
        target_type=target.target_type,
        description=target.description
    )
    db.add(new_target)
    db.commit()
    db.refresh(new_target)
    return new_target

@router.get("/", response_model=List[TargetResponse])
def read_targets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # FIX: Use 'Target' class
    targets_list = db.query(Target).offset(skip).limit(limit).all()
    return targets_list

@router.get("/{target_id}", response_model=TargetResponse)
def read_target(target_id: int, db: Session = Depends(get_db)):
    # FIX: Use 'Target' class
    target = db.query(Target).filter(Target.id == target_id).first()
    if target is None:
        raise HTTPException(status_code=404, detail="Target not found")
    return target

@router.delete("/{target_id}")
def delete_target(target_id: int, db: Session = Depends(get_db)):
    # FIX: Use 'Target' class
    target = db.query(Target).filter(Target.id == target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    
    db.delete(target)
    db.commit()
    return {"message": "Target deleted successfully"}