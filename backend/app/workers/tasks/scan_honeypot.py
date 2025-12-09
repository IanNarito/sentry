from datetime import datetime
from backend.app.workers.celery import celery_app
from backend.app.core.logging import logger
from backend.app.core.database import SessionLocal
from backend.app.models.scan import Scan
from backend.app.services.honeypot_service import scan_honeypot
import socket

@celery_app.task(bind=True)
def scan_honeypot_task(self, target_str: str, scan_id: int):
    """
    Honeypot Detection Task
    """
    logger.info(f"Starting Honeypot Scan for: {target_str}")
    db = SessionLocal()
    
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if scan:
        scan.status = "running"
        db.commit()

    # Resolve Domain to IP first (Honeypot checks need raw socket connection)
    try:
        target_ip = socket.gethostbyname(target_str)
    except:
        target_ip = target_str

    try:
        count, verdict = scan_honeypot(db, scan_id, scan.target_id, target_ip)
        
        status = "completed"
        result_data = {
            "verdict": verdict,
            "ip_scanned": target_ip,
            "findings_created": count
        }

    except Exception as e:
        logger.error(f"Honeypot scan failed: {e}")
        status = "failed"
        result_data = {"error": str(e)}

    if scan:
        scan.status = status
        scan.result = result_data
        scan.completed_at = datetime.now()
        db.commit()
    
    db.close()
    return status