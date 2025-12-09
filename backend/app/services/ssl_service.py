import ssl
import socket
import datetime
from backend.app.models.finding import Finding

def scan_ssl(db, scan_id, target_id, target_domain):
    """
    Connects to the target via SSL and analyzes the certificate.
    """
    findings_count = 0
    info_data = {}
    
    # Context setup
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE # We want to fetch it even if it's bad to analyze it

    try:
        with socket.create_connection((target_domain, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=target_domain) as ssock:
                cert = ssock.getpeercert()
                
                # 1. Parse Dates
                # Format is usually 'May 20 12:00:00 2025 GMT'
                date_fmt = r'%b %d %H:%M:%S %Y %Z'
                not_after_str = cert['notAfter']
                not_before_str = cert['notBefore']
                
                expires_on = datetime.datetime.strptime(not_after_str, date_fmt)
                started_on = datetime.datetime.strptime(not_before_str, date_fmt)
                now = datetime.datetime.utcnow()
                
                days_left = (expires_on - now).days
                
                info_data = {
                    "issuer": dict(x[0] for x in cert['issuer']),
                    "subject": dict(x[0] for x in cert['subject']),
                    "expires_on": not_after_str,
                    "days_left": days_left,
                    "version": ssock.version()
                }

                # --- VULNERABILITY CHECKS ---

                # Check 1: Expired Certificate
                if now > expires_on:
                    db.add(Finding(
                        scan_id=scan_id, target_id=target_id,
                        title="SSL Certificate Expired",
                        severity="Critical",
                        description=f"The certificate expired on {not_after_str}.",
                        remediation="Renew the SSL certificate immediately."
                    ))
                    findings_count += 1
                
                # Check 2: Expiring Soon (< 30 days)
                elif days_left < 30:
                    db.add(Finding(
                        scan_id=scan_id, target_id=target_id,
                        title="SSL Certificate Expiring Soon",
                        severity="Medium",
                        description=f"The certificate expires in {days_left} days.",
                        remediation="Plan for renewal to avoid downtime."
                    ))
                    findings_count += 1
                    
                # Check 3: Self-Signed (Issuer == Subject)
                # Note: This logic works for simple self-signed certs.
                # In parsed certs, issuer and subject are tuples of tuples.
                if cert['issuer'] == cert['subject']:
                     db.add(Finding(
                        scan_id=scan_id, target_id=target_id,
                        title="Self-Signed Certificate Detected",
                        severity="High",
                        description="The certificate is self-signed and not trusted by browsers.",
                        remediation="Purchase a certificate from a trusted CA or use Let's Encrypt."
                    ))
                     findings_count += 1

                # Check 4: Weak Protocol (e.g., TLSv1.0 or TLSv1.1)
                # Modern is TLSv1.2 or TLSv1.3
                if ssock.version() in ['TLSv1', 'TLSv1.1']:
                    db.add(Finding(
                        scan_id=scan_id, target_id=target_id,
                        title=f"Weak TLS Protocol: {ssock.version()}",
                        severity="High",
                        description="The server supports older, vulnerable encryption protocols.",
                        remediation="Disable TLS 1.0/1.1 and enforce TLS 1.2 or higher."
                    ))
                    findings_count += 1

    except Exception as e:
        return 0, {"error": str(e)}

    db.commit()
    return findings_count, info_data