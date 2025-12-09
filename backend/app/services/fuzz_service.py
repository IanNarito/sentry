import requests
import os
from backend.app.models.finding import Finding

def run_directory_fuzzing(db, scan_id, target_id, base_url):
    """
    Brute-forces common paths to find hidden files.
    """
    # 1. Load Wordlist
    wordlist_path = os.path.join(os.path.dirname(__file__), "../wordlists/common.txt")
    if not os.path.exists(wordlist_path):
        return 0, "Error: Wordlist not found"

    with open(wordlist_path, "r") as f:
        paths = [line.strip() for line in f if line.strip()]

    found_paths = []
    findings_count = 0
    
    # 2. Iterate and Request
    # Use a session for speed (Keep-Alive)
    session = requests.Session()
    # Fake user agent to avoid basic blocking
    session.headers.update({"User-Agent": "Sentry/1.0"})

    for path in paths:
        url = f"{base_url}/{path}"
        try:
            # allow_redirects=False is important to detect 301/302 redirects properly
            res = session.get(url, timeout=3, allow_redirects=False, verify=False)
            
            # We care about 200 (OK), 301/302 (Redirect), 401/403 (Forbidden but exists)
            if res.status_code in [200, 301, 302, 401, 403]:
                found_paths.append({
                    "path": path,
                    "status": res.status_code,
                    "url": url
                })

                # If we find a sensitive file (200 OK), create a specific finding
                if res.status_code == 200 and path in ['.env', 'backup.sql', 'db.sql', 'docker-compose.yml']:
                     db.add(Finding(
                        scan_id=scan_id,
                        target_id=target_id,
                        title=f"Critical File Exposed: {path}",
                        severity="Critical",
                        description=f"A sensitive file was found at {url}. This may contain passwords or config secrets.",
                        remediation="Remove this file from the public web root immediately."
                    ))
                     findings_count += 1
                
                # If we find an Admin panel
                elif path in ['admin', 'wp-admin', 'dashboard'] and res.status_code in [200, 301, 302]:
                     db.add(Finding(
                        scan_id=scan_id,
                        target_id=target_id,
                        title=f"Admin Panel Detected: {path}",
                        severity="Medium",
                        description=f"An administrative login page was found at {url}.",
                        remediation="Ensure this panel is protected by MFA or IP whitelisting."
                    ))
                     findings_count += 1

        except Exception:
            continue

    db.commit()
    
    # Return summary for the scan result
    summary = f"Scanned {len(paths)} paths. Found {len(found_paths)} accessible items."
    return findings_count, summary, found_paths