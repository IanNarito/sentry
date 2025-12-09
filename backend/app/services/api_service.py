import requests
import json
from backend.app.models.finding import Finding

# Common locations for API docs
SWAGGER_PATHS = [
    "swagger.json",
    "openapi.json",
    "api/docs",
    "api/swagger.json",
    "v2/api-docs",
    "swagger-ui.html",
    "api/v1/swagger.json"
]

def scan_api(db, scan_id, target_id, base_url):
    """
    Scans for exposed API documentation and parses endpoints.
    """
    findings_count = 0
    found_docs = None
    endpoints = []

    # 1. Hunt for the Documentation
    for path in SWAGGER_PATHS:
        url = f"{base_url}/{path}"
        try:
            # Short timeout to speed things up
            res = requests.get(url, timeout=3, verify=False)
            
            if res.status_code == 200:
                # Check if it looks like Swagger JSON
                if "swagger" in res.text.lower() or "openapi" in res.text.lower():
                    found_docs = url
                    
                    # Create Finding for Exposed Docs
                    db.add(Finding(
                        scan_id=scan_id,
                        target_id=target_id,
                        title=f"API Documentation Exposed: {path}",
                        severity="Low",
                        description=f"Public API documentation found at {url}. This reveals backend logic to attackers.",
                        remediation="Restrict access to Swagger/OpenAPI docs to internal networks only."
                    ))
                    findings_count += 1
                    
                    # 2. Parse the JSON to list endpoints (If content is JSON)
                    try:
                        data = res.json()
                        paths = data.get('paths', {})
                        for endpoint, methods in paths.items():
                            for method in methods:
                                endpoints.append(f"{method.upper()} {endpoint}")
                        
                        # Limit findings to avoid spamming database
                        preview = ", ".join(endpoints[:5])
                        total_endpoints = len(endpoints)
                        
                        db.add(Finding(
                            scan_id=scan_id,
                            target_id=target_id,
                            title=f"API Endpoints Discovered ({total_endpoints})",
                            severity="Info",
                            description=f"Successfully parsed {total_endpoints} API endpoints.\nPreview: {preview}...",
                            remediation="Review exposed endpoints for authentication requirements."
                        ))
                        findings_count += 1
                        
                        # Stop after finding the first valid doc file
                        break 
                    except json.JSONDecodeError:
                        # It might be HTML (Swagger UI), not JSON
                        pass
                        
        except Exception:
            continue

    db.commit()
    return findings_count, found_docs, endpoints