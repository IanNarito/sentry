from datetime import datetime
from backend.app.workers.celery import celery_app
from backend.app.core.logging import logger
from backend.app.core.database import SessionLocal
from backend.app.models.scan import Scan
from backend.app.services.waf_service import detect_waf

@celery_app.task(bind=True)
def scan_waf_task(self, target_str: str, scan_id: int):
    """
    WAF Detection Task
    """
    logger.info(f"Starting WAF Scan for: {target_str}")
    db = SessionLocal()
    
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if scan:
        scan.status = "running"
        db.commit()

    # WAFW00F handles the connection, but expects a URL
    target_url = f"https://{target_str}"

    try:
        count, waf_name = detect_waf(db, scan_id, scan.target_id, target_url)
        
        status = "completed"
        result_data = {
            "url": target_url,
            "waf_detected": waf_name,
            "findings": count
        }
        logger.info(f"WAF Scan Complete. Result: {waf_name}")

    except Exception as e:
        logger.error(f"WAF scan failed: {e}")
        status = "failed"
        result_data = {"error": str(e)}

    if scan:
        scan.status = status
        scan.result = result_data
        scan.completed_at = datetime.now()
        db.commit()
    
    db.close()
    return status