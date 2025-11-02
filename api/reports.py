"""
PDF Report Generation for Fraud Alerts
"""
from datetime import datetime
from io import BytesIO
from models import Alert
import json

# WeasyPrint is optional - will generate HTML reports if not available
try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False


def generate_pdf_report(alert: Alert) -> bytes:
    """
    Generate a PDF analyst report for a fraud alert
    """
    
    # HTML template
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Fraud Alert Report - {alert.alert_id}</title>
        <style>
            @page {{
                size: A4;
                margin: 2cm;
            }}
            body {{
                font-family: 'Segoe UI', Arial, sans-serif;
                color: #333;
                line-height: 1.6;
            }}
            .header {{
                border-bottom: 3px solid #dc2626;
                padding-bottom: 20px;
                margin-bottom: 30px;
            }}
            .header h1 {{
                color: #dc2626;
                margin: 0;
                font-size: 28px;
            }}
            .header .subtitle {{
                color: #666;
                font-size: 14px;
                margin-top: 5px;
            }}
            .risk-badge {{
                display: inline-block;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
                margin: 10px 0;
            }}
            .risk-critical {{
                background-color: #dc2626;
                color: white;
            }}
            .risk-high {{
                background-color: #ea580c;
                color: white;
            }}
            .risk-medium {{
                background-color: #f59e0b;
                color: white;
            }}
            .risk-low {{
                background-color: #10b981;
                color: white;
            }}
            .section {{
                margin-bottom: 25px;
            }}
            .section-title {{
                font-size: 18px;
                font-weight: bold;
                color: #1f2937;
                border-bottom: 2px solid #e5e7eb;
                padding-bottom: 8px;
                margin-bottom: 15px;
            }}
            .info-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 15px;
            }}
            .info-item {{
                padding: 12px;
                background: #f9fafb;
                border-left: 3px solid #3b82f6;
            }}
            .info-label {{
                font-size: 12px;
                color: #6b7280;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            .info-value {{
                font-size: 16px;
                font-weight: 600;
                color: #1f2937;
                margin-top: 4px;
            }}
            .rules-list {{
                list-style: none;
                padding: 0;
            }}
            .rules-list li {{
                padding: 10px;
                margin: 8px 0;
                background: #fef2f2;
                border-left: 4px solid #dc2626;
                font-size: 14px;
            }}
            .features-table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
            }}
            .features-table th {{
                background: #1f2937;
                color: white;
                padding: 10px;
                text-align: left;
                font-size: 12px;
                text-transform: uppercase;
            }}
            .features-table td {{
                padding: 10px;
                border-bottom: 1px solid #e5e7eb;
                font-size: 14px;
            }}
            .features-table tr:hover {{
                background: #f9fafb;
            }}
            .score-display {{
                text-align: center;
                padding: 20px;
                background: linear-gradient(135deg, #dc2626 0%, #ea580c 100%);
                color: white;
                border-radius: 8px;
                margin: 20px 0;
            }}
            .score-display .score-value {{
                font-size: 48px;
                font-weight: bold;
            }}
            .score-display .score-label {{
                font-size: 14px;
                opacity: 0.9;
                margin-top: 5px;
            }}
            .explanation-box {{
                background: #fffbeb;
                border: 1px solid #fbbf24;
                border-radius: 6px;
                padding: 15px;
                margin: 15px 0;
            }}
            .explanation-box p {{
                margin: 0;
                color: #78350f;
                font-size: 14px;
                line-height: 1.8;
            }}
            .footer {{
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #e5e7eb;
                text-align: center;
                color: #6b7280;
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚨 Fraud Alert Report</h1>
            <div class="subtitle">
                Alert ID: {alert.alert_id} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
            </div>
        </div>

        <div class="section">
            <div class="score-display">
                <div class="score-value">{alert.score:.2%}</div>
                <div class="score-label">FRAUD PROBABILITY SCORE</div>
            </div>
            <div style="text-align: center;">
                <span class="risk-badge risk-{alert.risk_level.lower()}">
                    {alert.risk_level} RISK
                </span>
            </div>
        </div>

        <div class="section">
            <div class="section-title">Transaction Details</div>
            <div class="info-grid">
                <div class="info-item">
                    <div class="info-label">Transaction ID</div>
                    <div class="info-value">{alert.txn_id}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Card ID</div>
                    <div class="info-value">{alert.card_id}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Merchant</div>
                    <div class="info-value">{alert.merchant_name}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Amount</div>
                    <div class="info-value">${alert.amount:,.2f}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Timestamp</div>
                    <div class="info-value">{alert.timestamp}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Status</div>
                    <div class="info-value">{alert.status}</div>
                </div>
            </div>
        </div>

        <div class="section">
            <div class="section-title">Triggered Rules</div>
            {f'<ul class="rules-list">' + ''.join([f'<li>✓ {rule.replace("_", " ").title()}</li>' for rule in alert.rules]) + '</ul>' if alert.rules else '<p>No specific rules triggered. Detection based on ML model.</p>'}
        </div>

        <div class="section">
            <div class="section-title">Model Explanation</div>
            <div class="explanation-box">
                <p>{alert.explanation.text}</p>
            </div>
            
            {f'''<table class="features-table">
                <thead>
                    <tr>
                        <th>Feature</th>
                        <th>Value</th>
                        <th>Contribution</th>
                        <th>Impact</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join([f"""
                    <tr>
                        <td>{feature.name.replace('_', ' ').title()}</td>
                        <td>{feature.value:.2f}</td>
                        <td>{feature.contribution:+.4f}</td>
                        <td>{feature.contribution_pct:.1f}%</td>
                    </tr>
                    """ for feature in alert.explanation.top_features[:5]])}
                </tbody>
            </table>''' if alert.explanation.top_features else ''}
        </div>

        <div class="section">
            <div class="section-title">Recommended Actions</div>
            <ol style="line-height: 2;">
                <li><strong>Contact cardholder</strong> immediately to verify the transaction</li>
                <li><strong>Temporarily suspend card</strong> to prevent further unauthorized charges</li>
                <li><strong>Review recent transactions</strong> on this card for additional fraud</li>
                <li><strong>Investigate merchant</strong> {alert.merchant_name} for suspicious activity</li>
                <li><strong>Update case status</strong> once investigation is complete</li>
            </ol>
        </div>

        <div class="footer">
            <p>
                <strong>FinGuard AI Fraud Detection System</strong><br>
                This report is confidential and intended for authorized personnel only.<br>
                For questions, contact: fraud-ops@finguard.ai
            </p>
        </div>
    </body>
    </html>
    """
    
    # Generate PDF if WeasyPrint is available, otherwise return HTML
    if WEASYPRINT_AVAILABLE:
        pdf_file = BytesIO()
        HTML(string=html_content).write_pdf(pdf_file)
        return pdf_file.getvalue()
    else:
        # Return HTML as bytes (can be viewed in browser)
        return html_content.encode('utf-8')

