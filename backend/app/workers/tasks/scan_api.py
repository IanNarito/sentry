from datetime import datetime
from backend.app.workers.celery import celery_app
from backend.app.core.logging import logger
from backend.app.core.database import SessionLocal
from backend.app.models.scan import Scan
from backend.app.services.api_service import scan_api
import urllib3

urllib3.disable_warnings()

@celery_app.task(bind=True)
def scan_api_task(self, target_str: str, scan_id: int):
    """
    API Discovery Task
    """
    logger.info(f"Starting API Scan for: {target_str}")
    db = SessionLocal()
    
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if scan:
        scan.status = "running"
        db.commit()

    # Default to HTTPS
    target_url = f"https://{target_str}"

    try:
        count, doc_url, endpoints = scan_api(db, scan_id, scan.target_id, target_url)
        
        # Fallback to HTTP if nothing found via HTTPS
        if not doc_url:
            target_url_http = f"http://{target_str}"
            count_http, doc_url_http, endpoints_http = scan_api(db, scan_id, scan.target_id, target_url_http)
            if doc_url_http:
                count += count_http
                doc_url = doc_url_http
                endpoints = endpoints_http

        status = "completed"
        result_data = {
            "docs_url": doc_url or "Not Found",
            "endpoints_count": len(endpoints),
            "endpoints_preview": endpoints[:10] if endpoints else []
        }

    except Exception as e:
        logger.error(f"API scan failed: {e}")
        status = "failed"
        result_data = {"error": str(e)}

    if scan:
        scan.status = status
        scan.result = result_data
        scan.completed_at = datetime.now()
        db.commit()
    
    db.close()
    return status