import nmap
from datetime import datetime
from backend.app.workers.celery import celery_app
from backend.app.core.logging import logger
from backend.app.core.database import SessionLocal
from backend.app.models.scan import Scan
from backend.app.models.target import Target
from backend.app.services.vuln_service import analyze_nmap_results

@celery_app.task(bind=True)
def scan_ports_task(self, target_str: str, scan_id: int):
    """
    Runs an Nmap Port Scan (Top 100 ports) and saves results.
    """
    logger.info(f"Starting Port Scan for: {target_str} (ID: {scan_id})")
    
    db = SessionLocal()
    scan_record = db.query(Scan).filter(Scan.id == scan_id).first()
    if scan_record:
        scan_record.status = "running"
        db.commit()

    nm = nmap.PortScanner()
    result_data = {}
    status = "failed"

    try:
        # Run the scan (arguments: -F = Fast Mode/Top 100 ports, -sV = Service Version)
        # We assume the target is up.
        logger.info("Launching Nmap process...")
        nm.scan(hosts=target_str, arguments='-F -sV')
        
        # Parse the complex Nmap output into simple JSON
        open_ports = []
        
        # Loop through protocols (tcp/udp)
        for host in nm.all_hosts():
            if 'tcp' in nm[host]:
                for port, details in nm[host]['tcp'].items():
                    if details['state'] == 'open':
                        open_ports.append({
                            "port": port,
                            "service": details.get('name', 'unknown'),
                            "version": details.get('version', ''),
                            "product": details.get('product', '')
                        })

        result_data = {
            "target": target_str,
            "open_ports": open_ports,
            "total_open": len(open_ports),
            "raw_output": "Scan complete"
        }
        status = "completed"
        logger.info(f"Port Scan Success. Found {len(open_ports)} open ports.")
        vuln_count = analyze_nmap_results(db, scan_id, scan_record.target_id, result_data)
        logger.info(f"Analysis Complete. Created {vuln_count} findings.")

    except Exception as e:
        logger.error(f"Nmap failed: {str(e)}")
        result_data = {"error": str(e), "hint": "Is Nmap installed and in PATH?"}
        status = "failed"

    if scan_record:
        scan_record.status = status
        scan_record.result = result_data
        scan_record.completed_at = datetime.now()
        db.commit()
    
    db.close()
    return status