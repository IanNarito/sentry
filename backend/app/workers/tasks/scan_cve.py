from datetime import datetime
from backend.app.workers.celery import celery_app
from backend.app.core.logging import logger
from backend.app.core.database import SessionLocal
from backend.app.models.scan import Scan
from backend.app.services.cve_service import scan_cve

@celery_app.task(bind=True)
def scan_cve_task(self, target_str: str, scan_id: int):
    """
    CVE Lookup Task
    """
    logger.info(f"Starting CVE Scan for: {target_str}")
    db = SessionLocal()
    
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if scan:
        scan.status = "running"
        db.commit()

    try:
        count, summary = scan_cve(db, scan_id, scan.target_id, target_str)
        
        status = "completed"
        result_data = {
            "summary": summary,
            "findings_created": count
        }

    except Exception as e:
        logger.error(f"CVE scan failed: {e}")
        status = "failed"
        result_data = {"error": str(e)}

    if scan:
        scan.status = status
        scan.result = result_data
        scan.completed_at = datetime.now()
        db.commit()
    
    db.close()
    return status