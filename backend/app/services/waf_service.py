from wafw00f.main import WAFW00F
from backend.app.models.finding import Finding

def detect_waf(db, scan_id, target_id, target_url):
    """
    Uses WAFW00F to detect if a Web Application Firewall is present.
    """
    # 1. Initialize WAFW00F
    # The modern library handles the target URL directly in the constructor
    waf = WAFW00F(target_url)
    
    # 2. Run Detection
    # The new method is simply called 'ident_waf' in some versions, but 
    # if that failed, we likely have a version that returns the list directly 
    # via the .ident_waf() method of the object, OR we need to inspect the attributes.
    
    # Let's try the safe, standard way for the newest version:
    detected_waf = "None"
    findings_count = 0
    
    try:
        # This scans for WAFs and returns a list of detected WAF names
        matches = waf.ident_waf() 
    except AttributeError:
        # Fallback for very new/different versions: manually inspect
        # Sometimes you have to inspect waf.waf_detections if ident_waf isn't exposed
        matches = None

    if matches:
        waf_name = ", ".join(matches)
        
        # Create a Finding
        db.add(Finding(
            scan_id=scan_id,
            target_id=target_id,
            title=f"WAF Detected: {waf_name}",
            severity="Info",
            description=f"The target is protected by: {waf_name}.",
            remediation="WAFs can block scanning attempts. Adjust scan rates."
        ))
        findings_count += 1
        detected_waf = waf_name
        
    else:
        # Try generic detection
        if waf.genericdetect():
            detected_waf = "Generic/Unknown WAF"
            db.add(Finding(
                scan_id=scan_id,
                target_id=target_id,
                title="Generic WAF Detected",
                severity="Info",
                description="A generic firewall was detected, but the vendor is unknown.",
                remediation="Proceed with caution."
            ))
            findings_count += 1

    db.commit()
    return findings_count, detected_waf