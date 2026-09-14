"""
Automated Intelligence Report Generation Service for Sentinel-X.
Exports threat analysis results to JSON, CSV, and formatted PDF intelligence reports.
"""
import json
import pandas as pd
from datetime import datetime
from utils.logging_utils import get_logger

logger = get_logger("report_service")

def generate_json_report(analysis_data: dict) -> str:
    """Generate structured JSON intelligence report."""
    report_payload = {
        "metadata": {
            "platform": "Sentinel-X OSINT Threat Intelligence Platform",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "report_version": "2.0"
        },
        "analysis_results": analysis_data
    }
    return json.dumps(report_payload, indent=2)

def generate_pdf_report(analysis_data: dict) -> bytes:
    """
    Generate PDF Intelligence Report using ReportLab if available.
    Falls back to text/markdown bytes if ReportLab is not installed.
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        import io

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=20, textColor=colors.HexColor('#1E293B'), spaceAfter=12)
        heading_style = ParagraphStyle('HeadingStyle', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#0F172A'), spaceBefore=10, spaceAfter=6)
        body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#334155'), spaceAfter=6)
        alert_style = ParagraphStyle('AlertStyle', parent=styles['Normal'], fontSize=11, textColor=colors.HexColor('#DC2626'), spaceAfter=6, fontName='Helvetica-Bold')

        story = []

        # Title Banner
        story.append(Paragraph("🛡️ SENTINEL-X INTELLIGENCE REPORT", title_style))
        story.append(Paragraph(f"<b>Generated At:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | <b>Classification:</b> OSINT Threat Analysis", body_style))
        story.append(Spacer(1, 12))

        # Executive Summary Table
        risk_score = analysis_data.get("risk_score", 0.0)
        risk_cat = analysis_data.get("risk_category", "Low")

        summary_data = [
            ["Metric", "Value"],
            ["Overall Risk Score", f"{risk_score} / 100"],
            ["Risk Category", risk_cat],
            ["Input Type", analysis_data.get("input_type", "Text Payload")]
        ]
        t = Table(summary_data, colWidths=[200, 300])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (1,0), colors.HexColor('#0F172A')),
            ('TEXTCOLOR', (0,0), (1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F8FAFC')),
            ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#E2E8F0'))
        ]))
        story.append(t)
        story.append(Spacer(1, 14))

        # Reasons Breakdown
        story.append(Paragraph("Executive Summary & Reason Breakdown", heading_style))
        reasons = analysis_data.get("reasons", [])
        for reason in reasons:
            story.append(Paragraph(f"• {reason}", body_style))
        story.append(Spacer(1, 10))

        # Detected Threat & Weapon Indicators
        story.append(Paragraph("Threat & Weapon Indicators", heading_style))
        t_details = analysis_data.get("threat_details", {})
        t_matches = t_details.get("threat_matches", []) + t_details.get("weapon_matches", []) + t_details.get("radicalization_matches", [])
        if t_matches:
            story.append(Paragraph(f"<b>Matches Identified:</b> {', '.join(t_matches)}", alert_style))
        else:
            story.append(Paragraph("No severe threat indicator keywords detected.", body_style))
        story.append(Spacer(1, 10))

        # Extracted Entities
        story.append(Paragraph("Extracted Named Entities (spaCy NER)", heading_style))
        e_details = analysis_data.get("entity_details", {})
        by_type = e_details.get("by_type", {})
        for etype, elist in by_type.items():
            if elist:
                story.append(Paragraph(f"<b>{etype}:</b> {', '.join(elist)}", body_style))
        story.append(Spacer(1, 14))

        # Footer Disclaimer
        story.append(Paragraph("<i>Disclaimer: Generated automatically by Sentinel-X OSINT Threat Intelligence Platform for analyst assistance.</i>", body_style))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    except Exception as e:
        logger.warning(f"ReportLab PDF generation fallback triggered: {e}")
        # Plain text fallback
        text_report = f"""
=====================================================
🛡️ SENTINEL-X OSINT INTELLIGENCE REPORT
=====================================================
Generated At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Risk Score: {analysis_data.get('risk_score', 0.0)} / 100
Risk Category: {analysis_data.get('risk_category', 'Low')}

Executive Reasons:
{chr(10).join(['- ' + r for r in analysis_data.get('reasons', [])])}

Threat Indicators:
{', '.join(analysis_data.get('threat_details', {}).get('threat_matches', ['None']))}

Extracted Entities:
{json.dumps(analysis_data.get('entity_details', {}).get('by_type', {}), indent=2)}

=====================================================
Sentinel-X Analyst Platform
=====================================================
"""
        return text_report.encode("utf-8")
