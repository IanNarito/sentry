from io import BytesIO
from xhtml2pdf import pisa
from jinja2 import Template
from datetime import datetime
from backend.app.models.target import Target
from backend.app.models.scan import Scan
from backend.app.models.finding import Finding
import os

# --- PROFESSIONAL PDF TEMPLATE (FIXED CSS) ---
PDF_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        /* --- GLOBAL STYLES --- */
        @page {
            size: A4;
            margin: 2cm;
        }
        body {
            font-family: Helvetica, Arial, sans-serif;
            color: #2c3e50;
            line-height: 1.6;
        }
        h1, h2, h3, h4 { color: #2c3e50; }
        a { color: #3498db; text-decoration: none; }
        
        /* --- UTILITIES --- */
        .page-break { page-break-before: always; }
        .text-right { text-align: right; }
        .text-center { text-align: center; }
        .bold { font-weight: bold; }

        /* --- COVER PAGE --- */
        #cover-page {
            text-align: center;
            padding-top: 150px;
        }
        #cover-page h1 {
            font-size: 48pt;
            color: #2c3e50;
            margin-bottom: 10px;
            letter-spacing: 2px;
        }
        #cover-page .subtitle {
            font-size: 18pt;
            color: #7f8c8d;
            margin-bottom: 100px;
            text-transform: uppercase;
        }
        #cover-page .report-meta {
            font-size: 14pt;
            color: #34495e;
            margin-top: 50px;
            padding: 30px;
            border-top: 2px solid #3498db;
            border-bottom: 2px solid #3498db;
            display: inline-block;
        }

        /* --- EXECUTIVE SUMMARY --- */
        .summary-box {
            background-color: #ecf0f1;
            padding: 25px;
            border-radius: 8px;
            border-left: 5px solid #3498db;
            margin-bottom: 30px;
        }
        .summary-grid td { padding: 10px 20px; }
        .summary-stat { font-size: 24pt; font-weight: bold; color: #2c3e50; display: block; }
        .summary-label { font-size: 10pt; color: #7f8c8d; text-transform: uppercase; }

        /* --- SEVERITY BADGES --- */
        .badge { padding: 5px 10px; border-radius: 4px; color: white; font-size: 9pt; font-weight: bold; text-transform: uppercase; }
        .Critical { background-color: #c0392b; }
        .High { background-color: #e67e22; }
        .Medium { background-color: #f1c40f; color: #2c3e50; }
        .Low { background-color: #27ae60; }
        .Info { background-color: #3498db; }

        /* --- DETAILED FINDINGS BLOCKS --- */
        .finding-block {
            border: 1px solid #bdc3c7;
            border-radius: 8px;
            margin-bottom: 25px;
            overflow: hidden;
            page-break-inside: avoid;
        }
        .finding-header {
            background-color: #f8f9fa;
            padding: 15px 20px;
            border-bottom: 1px solid #bdc3c7;
        }
        .finding-title { font-size: 14pt; font-weight: bold; margin: 0 0 5px 0; }
        .finding-meta { font-size: 9pt; color: #7f8c8d; }
        .finding-body { padding: 20px; }
        .section-label { 
            font-size: 10pt; 
            font-weight: bold; 
            color: #34495e; 
            text-transform: uppercase; 
            margin-bottom: 5px;
            margin-top: 15px;
            display: block;
        }
        .section-content { 
            font-size: 10pt; 
            color: #2c3e50; 
            background-color: #fafafa;
            padding: 10px;
            border-radius: 4px;
            border-left: 3px solid #bdc3c7;
        }

        /* --- TABLES --- */
        .data-table { width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 10pt; }
        .data-table th { background-color: #2c3e50; color: white; text-align: left; padding: 12px; text-transform: uppercase; font-size: 9pt; }
        .data-table td { border-bottom: 1px solid #ecf0f1; padding: 12px; }
        .data-table tr:nth-child(even) { background-color: #f8f9fa; }
        
        #footer {
            position: fixed;
            bottom: -1cm;
            left: 0cm;
            right: 0cm;
            height: 2cm;
            text-align: center;
            color: #7f8c8d;
            font-size: 9pt;
        }
    </style>
</head>
<body>
    <div id="footer">
        SENTRY Confidential Report | Generated on {{ date_only }}
    </div>

    <div id="cover-page">
        <h1>SENTRY</h1>
        <div class="subtitle">Security Reconnaissance Report</div>
        
        <div class="report-meta">
            <div><span class="bold">Target Scope:</span> {{ target.name }}</div>
            <div style="margin-top: 10px;"><span class="bold">Assessment Date:</span> {{ date_only }}</div>
        </div>
        
        <div style="margin-top: 150px; font-size: 10pt; color: #95a5a6;">
            CONFIDENTIAL DOCUMENT<br>
            Generated automatically by Sentry Platform.
        </div>
    </div>

    <div class="page-break"></div>

    <h2>Executive Summary</h2>
    <div class="summary-box">
        <table class="summary-grid" width="100%">
            <tr>
                <td align="center">
                    <span class="summary-stat">{{ target.target_type|capitalize }}</span>
                    <span class="summary-label">Asset Type</span>
                </td>
                <td align="center" style="border-left: 1px solid #bdc3c7; border-right: 1px solid #bdc3c7;">
                    <span class="summary-stat">{{ scan_count }}</span>
                    <span class="summary-label">Total Scans Run</span>
                </td>
                <td align="center">
                    <span class="summary-stat" style="color: {% if findings|length > 0 %}#c0392b{% else %}#27ae60{% endif %};">
                        {{ findings|length }}
                    </span>
                    <span class="summary-label">Vulnerabilities Identified</span>
                </td>
            </tr>
        </table>
    </div>

    <h2>Detailed Findings</h2>
    {% if findings %}
        {% for finding in findings %}
        <div class="finding-block">
            <div class="finding-header">
                <div style="float: right;"><span class="badge {{ finding.severity }}">{{ finding.severity }}</span></div>
                <h3 class="finding-title">{{ finding.title }}</h3>
                <div class="finding-meta">Finding ID: #{{ finding.id }} | Detected: {{ finding.created_at.strftime('%Y-%m-%d') }}</div>
            </div>
            <div class="finding-body">
                <span class="section-label">Description / Technical Details</span>
                <div class="section-content">
                    {{ finding.description | replace('\n', '<br/>') | safe }}
                </div>
                
                {% if finding.remediation %}
                <span class="section-label" style="color: #27ae60;">Recommended Remediation</span>
                <div class="section-content" style="border-left-color: #27ae60; background-color: #f0faf3;">
                    {{ finding.remediation | replace('\n', '<br/>') | safe }}
                </div>
                {% endif %}
            </div>
        </div>
        {% endfor %}
    {% else %}
        <div style="padding: 30px; text-align: center; background-color: #f8f9fa; border-radius: 8px; color: #7f8c8d;">
            <h3>No Vulnerabilities Detected</h3>
            <p>No significant security issues were identified during this assessment period based on the configured scans.</p>
        </div>
    {% endif %}

    <div class="page-break"></div>

    <h2>Appendix A: Scan Activity History</h2>
    <table class="data-table">
        <thead>
            <tr>
                <th>Timestamp (UTC)</th>
                <th>Module</th>
                <th>Status</th>
                <th>Outcome Summary</th>
            </tr>
        </thead>
        <tbody>
            {% for scan in scans %}
            <tr>
                <td>{{ scan.created_at.strftime('%Y-%m-%d %H:%M') }}</td>
                <td><strong>{{ scan.scan_type }}</strong></td>
                <td>
                    {% if scan.status == 'completed' %}<span style="color:#27ae60;">Completed</span>
                    {% elif scan.status == 'failed' %}<span style="color:#c0392b;">Failed</span>
                    {% else %}{{ scan.status|capitalize }}{% endif %}
                </td>
                <td style="font-family: monospace; font-size: 8pt;">
                    {% if scan.result %}
                        {% if scan.result.open_ports %} Open Ports: {{ scan.result.open_ports|length }}
                        {% elif scan.result.subdomains %} Subdomains: {{ scan.result.subdomains|length }}
                        {% elif scan.result.waf_detected %} WAF: {{ scan.result.waf_detected }}
                        {% elif scan.result.ssl_info and scan.result.ssl_info.expires_on %} Expires: {{ scan.result.ssl_info.expires_on[:11] }}
                        {% elif scan.result.ssl_info and scan.result.ssl_info.error %} SSL Error: {{ scan.result.ssl_info.error }}
                        {% elif scan.result.summary %} {{ scan.result.summary }}
                        {% else %} Data captured
                        {% endif %}
                    {% else %} - {% endif %}
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
"""

def generate_pdf_report(db, target_id):
    target = db.query(Target).filter(Target.id == target_id).first()
    if not target:
        return None

    scans = db.query(Scan).filter(Scan.target_id == target_id).order_by(Scan.created_at.desc()).all()
    findings = db.query(Finding).filter(Finding.target_id == target_id).order_by(Finding.severity.desc()).all()

    # Render HTML
    template = Template(PDF_TEMPLATE)
    html_content = template.render(
        target=target,
        date_only=datetime.now().strftime("%B %d, %Y"), # e.g., October 25, 2023
        scan_count=len(scans),
        scans=scans,
        findings=findings
    )

    # Convert to PDF
    pdf_file = BytesIO()
    # Use link_callback if you ever want to embed local images
    pisa_status = pisa.CreatePDF(html_content, dest=pdf_file)
    
    if pisa_status.err:
        print(f"PDF Generation Error: {pisa_status.err}")
        return None
    
    pdf_file.seek(0)
    return pdf_file