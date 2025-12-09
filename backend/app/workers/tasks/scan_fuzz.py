from datetime import datetime
from backend.app.workers.celery import celery_app
from backend.app.core.logging import logger
from backend.app.core.database import SessionLocal
from backend.app.models.scan import Scan
from backend.app.services.fuzz_service import run_directory_fuzzing
import urllib3

urllib3.disable_warnings()

@celery_app.task(bind=True)
def scan_fuzz_task(self, target_str: str, scan_id: int):
    """
    Directory Fuzzing Task
    """
    logger.info(f"Starting Fuzzing Scan for: {target_str}")
    db = SessionLocal()
    
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if scan:
        scan.status = "running"
        db.commit()

    # Construct Base URL (Assume HTTPS, fallback handling logic usually in service, but we keep it simple)
    # Ideally, you'd check which port is open first. We'll default to HTTPS.
    target_url = f"https://{target_str}"

    try:
        count, summary, found_items = run_directory_fuzzing(db, scan_id, scan.target_id, target_url)
        
        status = "completed"
        result_data = {
            "base_url": target_url,
            "summary": summary,
            "found_paths": found_items
        }

    except Exception as e:
        logger.error(f"Fuzzing failed: {e}")
        status = "failed"
        result_data = {"error": str(e)}

    # Save
    if scan:
        scan.status = status
        scan.result = result_data
        scan.completed_at = datetime.now()
        db.commit()
    
    db.close()
    return status