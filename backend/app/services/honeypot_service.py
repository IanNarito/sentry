import socket
from backend.app.models.finding import Finding

# Known signatures of common honeypots
HONEYPOT_SIGNATURES = {
    "kippo": "SSH-2.0-OpenSSH_5.1p1 Debian-5",
    "cowrie": "SSH-2.0-OpenSSH_6.0p1 Debian-4+deb7u2",
    "dionaea": "Dionaea",
    "glastopf": "Glastopf"
}

def scan_honeypot(db, scan_id, target_id, target_ip):
    """
    Checks if the target exhibits honeypot behavior.
    """
    findings_count = 0
    evidence = []
    score = 0 # 0 = Safe, 100 = Definitely a Honeypot

    # Check 1: Banner Grabbing on Trap Ports
    # Honeypots often listen on 22 (SSH) and 21 (FTP) with fake banners
    trap_ports = [21, 22, 23, 80, 443, 445, 3306]
    open_ports = 0
    
    for port in trap_ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((target_ip, port))
            
            if result == 0:
                open_ports += 1
                # Try to grab banner
                try:
                    sock.send(b'Hello\r\n')
                    banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
                    
                    # Check against known signatures
                    for hp_name, sig in HONEYPOT_SIGNATURES.items():
                        if sig in banner:
                            score += 50
                            evidence.append(f"Port {port}: Matches {hp_name} signature ({banner})")
                except:
                    pass
            sock.close()
        except:
            pass

    # Check 2: "Too Open" Heuristic
    # If a server has 5+ common ports open simultaneously, it's suspicious
    if open_ports >= 5:
        score += 30
        evidence.append(f"Suspiciously high number of open trap ports ({open_ports}/7).")

    # Final Verdict
    status_text = "Target appears normal."
    
    if score > 0:
        if score >= 50:
            severity = "High"
            title = "Honeypot Detected"
            status_text = "CONFIRMED HONEYPOT"
        else:
            severity = "Low"
            title = "Possible Honeypot Activity"
            status_text = "Suspected Honeypot"

        db.add(Finding(
            scan_id=scan_id,
            target_id=target_id,
            title=title,
            severity=severity,
            description=f"Honeypot Score: {score}/100\nEvidence:\n" + "\n".join(evidence),
            remediation="Do not interact. This system is likely monitoring your activity."
        ))
        findings_count += 1
    
    db.commit()
    return findings_count, status_text