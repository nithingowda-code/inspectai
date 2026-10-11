import os
import json
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from backend.app.models.inspection import InspectionRecord
from backend.app.database.session import DATA_DIR

def generate_pdf_report(inspection: InspectionRecord, product_name: str = "Unassigned Product") -> str:
    """
    Generates a formal industrial inspection PDF certificate and returns the file path.
    """
    reports_dir = os.path.join(DATA_DIR, "reports")
    os.makedirs(reports_dir, exist_ok=True)
    report_filename = f"Inspection_Report_{inspection.id[:8]}.pdf"
    pdf_path = os.path.join(reports_dir, report_filename)

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0F172A')
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#475569')
    )
    section_title = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=10,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#334155')
    )

    story = []

    # Header
    story.append(Paragraph("INSPECT-AI // QUALITY ASSURANCE REPORT", title_style))
    story.append(Paragraph(f"Universal AI Optical Metrology & Surface Inspection System | Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}", subtitle_style))
    story.append(Spacer(1, 12))

    # Status Banner
    status_bg = colors.HexColor('#DC2626') if inspection.overall_status == "FAIL" else (
        colors.HexColor('#16A34A') if inspection.overall_status == "PASS" else colors.HexColor('#D97706')
    )
    status_data = [
        [
            Paragraph(f"<b>INSPECTION ID:</b> {inspection.id}", body_style),
            Paragraph(f"<b>OVERALL STATUS:</b> <font color='white'><b>{inspection.overall_status}</b></font>", ParagraphStyle('StatusCell', parent=body_style, textColor=colors.white))
        ]
    ]
    status_table = Table(status_data, colWidths=[340, 200])
    status_table.setStyle(TableStyle([
        ('BACKGROUND', (1, 0), (1, 0), status_bg),
        ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#F1F5F9')),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
    ]))
    story.append(status_table)
    story.append(Spacer(1, 10))

    # Product & Inspection Details Table
    info_data = [
        [Paragraph("<b>Target Product:</b>", body_style), Paragraph(product_name, body_style),
         Paragraph("<b>Inspection Mode:</b>", body_style), Paragraph(inspection.mode.upper(), body_style)],
        [Paragraph("<b>Timestamp:</b>", body_style), Paragraph(inspection.created_at.strftime('%Y-%m-%d %H:%M:%S'), body_style),
         Paragraph("<b>Unit of Measure:</b>", body_style), Paragraph(inspection.unit, body_style)],
    ]
    info_table = Table(info_data, colWidths=[100, 170, 100, 170])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 12))

    # Executive Explanation
    story.append(Paragraph("<b>Executive Summary & Decision Rationale:</b>", section_title))
    story.append(Paragraph(inspection.overall_explanation, body_style))
    story.append(Spacer(1, 10))

    # Dimensional Metrology Section
    if inspection.measured_length is not None or inspection.measured_width is not None:
        story.append(Paragraph("<b>1. Dimensional Optical Metrology</b>", section_title))
        dim_data = [
            [Paragraph("<b>Dimension</b>", body_style), Paragraph("<b>Expected</b>", body_style),
             Paragraph("<b>Measured</b>", body_style), Paragraph("<b>Deviation</b>", body_style), Paragraph("<b>Result</b>", body_style)],
            [Paragraph("Length", body_style),
             Paragraph(f"{inspection.expected_length:.2f} {inspection.unit}" if inspection.expected_length else "N/A", body_style),
             Paragraph(f"{inspection.measured_length:.2f} {inspection.unit}" if inspection.measured_length else "N/A", body_style),
             Paragraph(f"{inspection.length_deviation:+.2f} {inspection.unit}" if inspection.length_deviation else "N/A", body_style),
             Paragraph(f"<b>{inspection.dimensional_status or 'N/A'}</b>", body_style)],
            [Paragraph("Width", body_style),
             Paragraph(f"{inspection.expected_width:.2f} {inspection.unit}" if inspection.expected_width else "N/A", body_style),
             Paragraph(f"{inspection.measured_width:.2f} {inspection.unit}" if inspection.measured_width else "N/A", body_style),
             Paragraph(f"{inspection.width_deviation:+.2f} {inspection.unit}" if inspection.width_deviation else "N/A", body_style),
             Paragraph(f"<b>{inspection.dimensional_status or 'N/A'}</b>", body_style)]
        ]
        dim_table = Table(dim_data, colWidths=[100, 110, 110, 110, 110])
        dim_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E2E8F0')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ]))
        story.append(dim_table)
        story.append(Spacer(1, 10))

    # Anomaly and Defect Detection Section
    story.append(Paragraph("<b>2. AI Visual Defect & Anomaly Analysis</b>", section_title))
    defects = json.loads(inspection.detected_defects_json or "[]")
    
    anomaly_summary_data = [
        [Paragraph("<b>Metric</b>", body_style), Paragraph("<b>Observed Value</b>", body_style), Paragraph("<b>Threshold / Criteria</b>", body_style), Paragraph("<b>Status</b>", body_style)],
        [Paragraph("Anomaly Score", body_style), Paragraph(f"{inspection.anomaly_score:.3f}" if inspection.anomaly_score is not None else "N/A", body_style), Paragraph(f"≤ {inspection.anomaly_threshold:.2f}" if inspection.anomaly_threshold else "N/A", body_style), Paragraph(f"<b>{inspection.anomaly_status or 'N/A'}</b>", body_style)],
        [Paragraph("Reference Similarity", body_style), Paragraph(f"{inspection.reference_similarity_score:.3f}" if inspection.reference_similarity_score is not None else "N/A", body_style), Paragraph("≥ 0.700", body_style), Paragraph(f"<b>{inspection.reference_status or 'N/A'}</b>", body_style)],
        [Paragraph("Detected Flaws Count", body_style), Paragraph(str(len(defects)), body_style), Paragraph("0 Permitted", body_style), Paragraph("PASS" if len(defects) == 0 else "FAIL", body_style)],
    ]
    anom_table = Table(anomaly_summary_data, colWidths=[140, 130, 140, 130])
    anom_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E2E8F0')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(anom_table)
    story.append(Spacer(1, 10))

    # Checks breakdown
    checks = json.loads(inspection.checks_executed_json or "[]")
    if checks:
        story.append(Paragraph("<b>3. Executed Quality Checkpoints</b>", section_title))
        checks_data = [[Paragraph("<b>Check Name</b>", body_style), Paragraph("<b>Executed</b>", body_style), Paragraph("<b>Status</b>", body_style), Paragraph("<b>Details</b>", body_style)]]
        for c in checks:
            checks_data.append([
                Paragraph(c.get("check_name", ""), body_style),
                Paragraph("YES" if c.get("executed") else "NO", body_style),
                Paragraph(f"<b>{c.get('status', '')}</b>", body_style),
                Paragraph(c.get("explanation", "")[:120], body_style)
            ])
        checks_table = Table(checks_data, colWidths=[150, 60, 70, 260])
        checks_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E2E8F0')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('PADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(checks_table)
        story.append(Spacer(1, 10))

    # Technical Disclaimers and Limitations
    limitations = json.loads(inspection.limitations_json or "[]")
    if limitations:
        story.append(Paragraph("<b>Technical Disclaimers & System Boundaries:</b>", section_title))
        for lim in limitations:
            story.append(Paragraph(f"• {lim}", ParagraphStyle('LimItem', parent=body_style, textColor=colors.HexColor('#64748B'))))
        story.append(Spacer(1, 10))

    # Sign-off footer
    story.append(Spacer(1, 15))
    sign_data = [
        [Paragraph("<b>Inspection Algorithm:</b> ResNet18 + OpenCV Metrology", subtitle_style),
         Paragraph("<b>Authorized Verification:</b> InspectAI System", subtitle_style)]
    ]
    sign_table = Table(sign_data, colWidths=[270, 270])
    story.append(sign_table)

    doc.build(story)
    return pdf_path
