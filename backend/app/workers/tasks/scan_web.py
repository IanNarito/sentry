from datetime import datetime
from backend.app.workers.celery import celery_app
from backend.app.core.logging import logger
from backend.app.core.database import SessionLocal
from backend.app.models.scan import Scan
from backend.app.services.web_service import analyze_web_headers

@celery_app.task(bind=True)
def scan_web_task(self, target_str: str, scan_id: int):
    """
    Performs Web Recon (Headers & Tech Detection)
    """
    logger.info(f"Starting Web Scan for: {target_str}")
    db = SessionLocal()
    
    # Update Status
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if scan:
        scan.status = "running"
        db.commit()

    # Determine URL (try HTTPS first, then HTTP)
    target_url = f"https://{target_str}"
    
    # Run Analysis
    count, info = analyze_web_headers(db, scan_id, scan.target_id, target_url)
    
    # If HTTPS failed, try HTTP
    if "Failed" in info:
        target_url = f"http://{target_str}"
        count, info = analyze_web_headers(db, scan_id, scan.target_id, target_url)

    # Save Result
    if scan:
        scan.status = "completed"
        scan.result = {
            "url": target_url,
            "tech_stack": info,
            "findings_created": count
        }
        scan.completed_at = datetime.now()
        db.commit()
    
    db.close()
    return "completed"