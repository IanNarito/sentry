import os
from datetime import datetime
from jinja2 import Template
from sqlalchemy.orm import Session
from backend.app.models.target import Target
from backend.app.models.scan import Scan
from backend.app.models.finding import Finding

REPORT_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>SENTRY Report - {{ target.name }}</title>
    <style>
        body { font-family: 'Courier New', monospace; background-color: #0a0a0a; color: #e0e0e0; padding: 40px; }
        .header { border-bottom: 2px solid #00ff41; padding-bottom: 20px; margin-bottom: 40px; }
        h1 { color: #00ff41; margin: 0; }
        .section { background: #111; border: 1px solid #333; padding: 20px; margin-bottom: 30px; border-radius: 8px; }
        h2 { color: #fff; border-bottom: 1px solid #333; padding-bottom: 10px; margin-top: 0; }
        .badge { padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
        .critical { background: #ff3333; color: white; }
        .high { background: #ffaa00; color: black; }
        .medium { background: #ffcc00; color: black; }
        .low { background: #33cc33; color: black; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { text-align: left; padding: 12px; border-bottom: 1px solid #333; }
        th { color: #888; font-size: 12px; text-transform: uppercase; }
    </style>
</head>
<body>
    <div class="header">
        <h1>SENTRY INTELLIGENCE REPORT</h1>
        <p>Target: <strong>{{ target.name }}</strong> ({{ target.target_type }})</p>
        <p>Generated: {{ generation_date }}</p>
    </div>

    <div class="section">
        <h2>Executive Summary</h2>
        <p>Total Scans Performed: {{ scan_count }}</p>
        <p>Total Vulnerabilities Found: <strong>{{ findings|length }}</strong></p>
    </div>

    <div class="section">
        <h2>Vulnerability Findings</h2>
        {% if findings %}
        <table>
            <thead>
                <tr>
                    <th>Severity</th>
                    <th>Issue</th>
                    <th>Description</th>
                </tr>
            </thead>
            <tbody>
                {% for finding in findings %}
                <tr>
                    <td><span class="badge {{ finding.severity|lower }}">{{ finding.severity }}</span></td>
                    <td>{{ finding.title }}</td>
                    <td>{{ finding.description }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% else %}
        <p style="color: #666;">No vulnerabilities detected.</p>
        {% endif %}
    </div>

    <div class="section">
        <h2>Recent Scan History</h2>
        <table>
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Type</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {% for scan in scans %}
                <tr>
                    <td>{{ scan.created_at.strftime('%Y-%m-%d %H:%M') }}</td>
                    <td>{{ scan.scan_type }}</td>
                    <td>{{ scan.status }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</body>
</html>
"""

def generate_target_report(db: Session, target_id: int):
    target = db.query(Target).filter(Target.id == target_id).first()
    if not target:
        return None

    scans = db.query(Scan).filter(Scan.target_id == target_id).order_by(Scan.created_at.desc()).all()
    findings = db.query(Finding).filter(Finding.target_id == target_id).order_by(Finding.severity.desc()).all()

    template = Template(REPORT_TEMPLATE)
    html_content = template.render(
        target=target,
        generation_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        scan_count=len(scans),
        scans=scans,
        findings=findings
    )
    
    return html_content