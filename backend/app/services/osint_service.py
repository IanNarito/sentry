import requests
import logging

logger = logging.getLogger("sentry")

def get_subdomains_crtsh(domain: str):
    """
    Queries crt.sh to find subdomains (Passive OSINT).
    Returns a list of unique subdomains.
    """
    url = f"https://crt.sh/?q=%.{domain}&output=json"
    subdomains = set()
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            for entry in data:
                name_value = entry['name_value']
                # Clean up newlines and split multiple domains
                for sub in name_value.split('\n'):
                    if "*" not in sub: # Ignore wildcards
                        subdomains.add(sub.lower())
        return list(subdomains)
    except Exception as e:
        logger.error(f"Error querying crt.sh: {e}")
        return []