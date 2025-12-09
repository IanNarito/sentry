import requests
import urllib3
from backend.app.models.finding import Finding

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def analyze_web_headers(db, scan_id, target_id, url):
    """
    Connects to a URL, grabs headers, and creates findings for security issues.
    """
    findings_count = 0
    try:
        # 1. Connect to the target (Time out after 5s, ignore SSL errors)
        response = requests.get(url, timeout=5, verify=False)
        headers = response.headers
        
        # 2. Tech Detection (Basic Fingerprinting)
        server_header = headers.get('Server', 'Unknown')
        x_powered_by = headers.get('X-Powered-By', 'Unknown')
        
        tech_info = f"Server: {server_header} | Technology: {x_powered_by}"
        
        # Create an INFO finding just to list the technology
        db.add(Finding(
            scan_id=scan_id,
            target_id=target_id,
            title=f"Web Technology Detected ({url})",
            severity="Info",
            description=f"Server: {server_header}\nFramework: {x_powered_by}\nStatus Code: {response.status_code}",
            remediation="Information disclosure only. Consider hiding version numbers in production."
        ))
        findings_count += 1

        # 3. Security Header Checks
        security_headers = {
            "X-Frame-Options": {"severity": "Low", "desc": "Missing Clickjacking protection."},
            "Strict-Transport-Security": {"severity": "Medium", "desc": "HSTS not enforced. Man-in-the-Middle attacks possible."},
            "X-Content-Type-Options": {"severity": "Low", "desc": "Missing MIME-sniffing protection."},
            "Content-Security-Policy": {"severity": "Medium", "desc": "No CSP detected. Vulnerable to XSS/Injection attacks."}
        }

        for header, info in security_headers.items():
            if header not in headers:
                db.add(Finding(
                    scan_id=scan_id,
                    target_id=target_id,
                    title=f"Missing Header: {header}",
                    severity=info['severity'],
                    description=f"The web server at {url} is not returning the '{header}' security header. {info['desc']}",
                    remediation=f"Configure the web server to send the {header} header."
                ))
                findings_count += 1
                
        db.commit()
        return findings_count, tech_info

    except requests.exceptions.RequestException as e:
        return 0, f"Failed to connect: {str(e)}"