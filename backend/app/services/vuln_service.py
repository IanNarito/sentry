from sqlalchemy.orm import Session
from backend.app.models.finding import Finding

def analyze_nmap_results(db: Session, scan_id: int, target_id: int, result_data: dict):
    """
    Analyzes Nmap JSON output and creates Findings for risky ports.
    """
    open_ports = result_data.get("open_ports", [])
    
    risky_ports = {
        21: {"severity": "Medium", "title": "Insecure FTP Service", "desc": "FTP transmits credentials in cleartext."},
        23: {"severity": "High", "title": "Telnet Service Detected", "desc": "Telnet is unencrypted and vulnerable to sniffing."},
        22: {"severity": "Info", "title": "SSH Service Open", "desc": "Ensure strict key-based authentication is enabled."},
        3389: {"severity": "Medium", "title": "RDP Exposed", "desc": "Remote Desktop Protocol exposed to the internet."},
        80: {"severity": "Info", "title": "HTTP Service", "desc": "Web server detected. Check for vulnerabilities."},
        445: {"severity": "High", "title": "SMB Service Exposed", "desc": "SMB can expose files and is a target for ransomware."}
    }

    findings_count = 0

    for port_info in open_ports:
        port = int(port_info['port'])
        
        if port in risky_ports:
            risk = risky_ports[port]
            finding = Finding(
                scan_id=scan_id,
                target_id=target_id,
                title=f"{risk['title']} (Port {port})",
                severity=risk['severity'],
                description=f"{risk['desc']} Service version: {port_info.get('version', 'unknown')}",
                remediation="Restrict access via firewall or disable service if not needed."
            )
            db.add(finding)
            findings_count += 1
            
    db.commit()
    return findings_count