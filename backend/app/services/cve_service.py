import requests
from backend.app.models.finding import Finding
import urllib3
import re

urllib3.disable_warnings()

def scan_cve(db, scan_id, target_id, target_str):
    """
    1. Detects Server Version (Banner Grabbing).
    2. Queries CVE database for known vulnerabilities.
    """
    findings_count = 0
    cve_data = []
    
    # 1. Grab Banner
    # We assume HTTP/HTTPS for now
    url = f"https://{target_str}"
    server_header = "Unknown"
    
    try:
        res = requests.get(url, timeout=5, verify=False)
        server_header = res.headers.get('Server', '')
    except:
        try:
            url = f"http://{target_str}"
            res = requests.get(url, timeout=5)
            server_header = res.headers.get('Server', '')
        except:
            return 0, "Failed to connect to target for banner grabbing."

    if not server_header or len(server_header) < 3:
        return 0, "No 'Server' header exposed by target. Cannot perform CVE lookup."

    # 2. Parse the Banner (e.g., "Apache/2.4.49 (Unix)" -> "Apache 2.4.49")
    # Simple regex to grab Product + Version
    # Looks for pattern like "Name/1.2.3"
    match = re.search(r'([a-zA-Z]+)/([\d\.]+)', server_header)
    
    if match:
        product = match.group(1).lower()
        version = match.group(2)
        search_query = f"{product} {version}"
        
        # 3. Query CIRCL CVE API
        # API: https://cve.circl.lu/api/search/<keywords>
        api_url = f"https://cve.circl.lu/api/search/{product}/{version}"
        
        try:
            # Using the specific browser search endpoint for better accuracy
            # Or general search: https://cve.circl.lu/api/search/apache/2.4.49
            cve_res = requests.get(api_url, timeout=10)
            
            if cve_res.status_code == 200:
                data = cve_res.json()
                # data is usually a list of CVE objects
                
                # Limit to Top 5 most recent/critical to avoid spamming
                for item in data[:5]:
                    cve_id = item.get('id')
                    summary = item.get('summary', 'No summary.')
                    cvss = item.get('cvss', 0)
                    
                    # Determine Severity based on CVSS
                    severity = "Low"
                    if cvss >= 9.0: severity = "Critical"
                    elif cvss >= 7.0: severity = "High"
                    elif cvss >= 4.0: severity = "Medium"
                    
                    cve_data.append(cve_id)
                    
                    db.add(Finding(
                        scan_id=scan_id,
                        target_id=target_id,
                        title=f"Known Vulnerability: {cve_id}",
                        severity=severity,
                        description=f"Product: {server_header}\nCVSS Score: {cvss}\nDetails: {summary}",
                        remediation="Update the software to the latest patched version."
                    ))
                    findings_count += 1
            
        except Exception as e:
            return findings_count, f"CVE API Error: {str(e)}"
            
        summary_text = f"Banner: {server_header}. Found {len(cve_data)} CVEs."
    else:
        summary_text = f"Banner found ({server_header}) but could not extract version number for CVE lookup."

    db.commit()
    return findings_count, summary_text