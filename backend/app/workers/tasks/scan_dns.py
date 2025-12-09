import socket
from datetime import datetime
from backend.app.workers.celery import celery_app
from backend.app.core.logging import logger
from backend.app.core.database import SessionLocal
from backend.app.models.scan import Scan
from backend.app.models.target import Target

@celery_app.task(bind=True)
def scan_dns_task(self, target_str: str, scan_id: int):
    """
    Performs DNS resolution and saves result to the Database.
    """
    logger.info(f"Starting DNS scan for: {target_str} (ID: {scan_id})")
    
    # 1. Open Database Session
    db = SessionLocal()
    
    # 2. Update Status to RUNNING
    scan_record = db.query(Scan).filter(Scan.id == scan_id).first()
    if scan_record:
        scan_record.status = "running"
        db.commit()

    result_data = {}
    status = "failed"

    try:
        # 3. Perform the actual Scan
        ip_address = socket.gethostbyname(target_str)
        
        result_data = {
            "target": target_str,
            "ip": ip_address,
            "record_type": "A"
        }
        status = "completed"
        logger.info(f"Scan Success: {result_data}")

    except Exception as e:
        logger.error(f"Scan failed: {str(e)}")
        result_data = {"error": str(e)}
        status = "failed"

    # 4. Save Final Result to DB
    if scan_record:
        scan_record.status = status
        scan_record.result = result_data
        scan_record.completed_at = datetime.now()
        db.commit()
    
    db.close()
    return status