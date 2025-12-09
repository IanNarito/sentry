from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime
from backend.app.core.database import get_db
from backend.app.models.scan import Scan
from backend.app.models.target import Target
from backend.app.workers.tasks.scan_dns import scan_dns_task
from backend.app.workers.tasks.scan_ports import scan_ports_task
from backend.app.workers.tasks.scan_osint import scan_subdomains_task
from backend.app.workers.tasks.scan_web import scan_web_task
from backend.app.workers.tasks.scan_whois import scan_whois_task
from backend.app.workers.tasks.scan_fuzz import scan_fuzz_task
from backend.app.workers.tasks.scan_waf import scan_waf_task
from backend.app.workers.tasks.scan_ssl import scan_ssl_task
from backend.app.workers.tasks.scan_api import scan_api_task
from backend.app.workers.tasks.scan_cve import scan_cve_task
from backend.app.workers.tasks.scan_honeypot import scan_honeypot_task

router = APIRouter()

# Input Schema
class ScanRequest(BaseModel):
    target_id: int
    scan_type: str = "DNS"

# Output Schema
class ScanResponse(BaseModel):
    id: int
    target_id: int
    scan_type: str
    status: str
    result: Optional[Any]
    created_at: datetime
    
    class Config:
        from_attributes = True

@router.post("/", response_model=ScanResponse)
def create_scan(request: ScanRequest, db: Session = Depends(get_db)):
    target = db.query(Target).filter(Target.id == request.target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")

    new_scan = Scan(
        target_id=target.id,
        scan_type=request.scan_type,
        status="pending"
    )
    db.add(new_scan)
    db.commit()
    db.refresh(new_scan)

    # DISPATCH LOGIC
    if request.scan_type == "NMAP":
        scan_ports_task.delay(target.name, new_scan.id)
    elif request.scan_type == "SUBDOMAIN":     
        scan_subdomains_task.delay(target.name, new_scan.id)
    elif request.scan_type == "WEB": 
        scan_web_task.delay(target.name, new_scan.id)
    elif request.scan_type == "WHOIS":      
        scan_whois_task.delay(target.name, new_scan.id)
    elif request.scan_type == "FUZZ":
        scan_fuzz_task.delay(target.name, new_scan.id)
    elif request.scan_type == "WAF":
        scan_waf_task.delay(target.name, new_scan.id)
    elif request.scan_type == "SSL":
        scan_ssl_task.delay(target.name, new_scan.id)
    elif request.scan_type == "API":
        scan_api_task.delay(target.name, new_scan.id)
    elif request.scan_type == "CVE":
        scan_cve_task.delay(target.name, new_scan.id)
    elif request.scan_type == "HONEYPOT":
        scan_honeypot_task.delay(target.name, new_scan.id)
    else:
        # Default to DNS
        scan_dns_task.delay(target.name, new_scan.id)
    
    return new_scan

@router.get("/", response_model=List[ScanResponse])
def get_scans(db: Session = Depends(get_db)):
    # Return all scans, newest first
    return db.query(Scan).order_by(Scan.created_at.desc()).all()

@router.post("/", response_model=ScanResponse)
def create_scan(request: ScanRequest, db: Session = Depends(get_db)):
    target = db.query(Target).filter(Target.id == request.target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")

    new_scan = Scan(
        target_id=target.id,
        scan_type=request.scan_type, # Use the requested type (DNS or NMAP)
        status="pending"
    )
    db.add(new_scan)
    db.commit()
    db.refresh(new_scan)

    # DISPATCH LOGIC
    if request.scan_type == "NMAP":
        scan_ports_task.delay(target.name, new_scan.id)
    else:
        # Default to DNS
        scan_dns_task.delay(target.name, new_scan.id)
    
    return new_scan