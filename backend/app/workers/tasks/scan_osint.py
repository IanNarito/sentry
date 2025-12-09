from datetime import datetime
from backend.app.workers.celery import celery_app
from backend.app.core.logging import logger
from backend.app.core.database import SessionLocal
from backend.app.models.scan import Scan
from backend.app.services.osint_service import get_subdomains_crtsh

@celery_app.task(bind=True)
def scan_subdomains_task(self, target_str: str, scan_id: int):
    """
    Passive Subdomain Enumeration Task
    """
    logger.info(f"Starting Subdomain Scan for: {target_str} (ID: {scan_id})")
    
    db = SessionLocal()
    scan_record = db.query(Scan).filter(Scan.id == scan_id).first()
    if scan_record:
        scan_record.status = "running"
        db.commit()

    result_data = {}
    status = "failed"

    try:
        # 1. Run the OSINT service
        subs = get_subdomains_crtsh(target_str)
        
        result_data = {
            "target": target_str,
            "subdomains": subs,
            "count": len(subs),
            "source": "crt.sh (Certificate Transparency)"
        }
        status = "completed"
        logger.info(f"Found {len(subs)} subdomains for {target_str}")

    except Exception as e:
        logger.error(f"OSINT scan failed: {str(e)}")
        result_data = {"error": str(e)}
        status = "failed"

    # 2. Save results
    if scan_record:
        scan_record.status = status
        scan_record.result = result_data
        scan_record.completed_at = datetime.now()
        db.commit()
    
    db.close()
    return status