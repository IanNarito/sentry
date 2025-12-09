import whois
from datetime import datetime
from backend.app.workers.celery import celery_app
from backend.app.core.logging import logger
from backend.app.core.database import SessionLocal
from backend.app.models.scan import Scan

@celery_app.task(bind=True)
def scan_whois_task(self, target_str: str, scan_id: int):
    """
    Performs WHOIS lookup to find domain registration details.
    """
    logger.info(f"Starting WHOIS Scan for: {target_str} (ID: {scan_id})")
    
    db = SessionLocal()
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if scan:
        scan.status = "running"
        db.commit()

    result_data = {}
    status = "failed"

    try:
        # Perform Lookup
        w = whois.whois(target_str)
        
        # Convert complex objects (like lists of dates) to strings for JSON
        def format_date(d):
            if isinstance(d, list):
                return str(d[0]) if d else None
            return str(d) if d else None

        result_data = {
            "registrar": w.registrar,
            "creation_date": format_date(w.creation_date),
            "expiration_date": format_date(w.expiration_date),
            "organization": w.org,
            "emails": w.emails,
            "name_servers": w.name_servers,
            "raw_text": "Lookup Successful"
        }
        
        status = "completed"
        logger.info(f"WHOIS Success: Registered to {w.org or 'Unknown'}")

    except Exception as e:
        logger.error(f"WHOIS failed: {str(e)}")
        result_data = {"error": str(e)}
        status = "failed"

    # Save Results
    if scan:
        scan.status = status
        scan.result = result_data
        scan.completed_at = datetime.now()
        db.commit()
    
    db.close()
    return status