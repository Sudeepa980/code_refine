"""
Generate downloadable PDF report for a code review.
"""
from io import BytesIO
from typing import List, Dict, Any, Optional


def generate_pdf(
    code: str,
    language: str,
    static_issues: List[Dict],
    time_complexity: str,
    space_complexity: str,
    time_reasons: List[Dict],
    space_reasons: List[Dict],
    quality_score: int,
    score_reasons: List[str],
    ai_explanation: Optional[str] = None,
    ai_bugs: Optional[str] = None,
) -> Optional[BytesIO]:
    """Returns PDF as BytesIO or None if reportlab not available."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted, Table, TableStyle, PageBreak
        from reportlab.lib import colors
    except ImportError:
        return None

    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle(name="Title", parent=styles["Heading1"], fontSize=18)
    story.append(Paragraph("CodeRefine – Code Review Report", title_style))
    story.append(Spacer(1, 0.25 * inch))
    story.append(Paragraph(f"<b>Language:</b> {language.upper()}", styles["Normal"]))
    story.append(Paragraph(f"<b>Quality Score:</b> {quality_score}/100", styles["Normal"]))
    story.append(Paragraph(f"<b>Time Complexity:</b> {time_complexity}", styles["Normal"]))
    story.append(Paragraph(f"<b>Space Complexity:</b> {space_complexity}", styles["Normal"]))
    story.append(Spacer(1, 0.2 * inch))

    story.append(Paragraph("Score breakdown", styles["Heading2"]))
    for r in score_reasons:
        story.append(Paragraph(f"• {r}", styles["Normal"]))
    story.append(Spacer(1, 0.2 * inch))

    story.append(Paragraph("Code", styles["Heading2"]))
    code_style = ParagraphStyle(name="CodeBlock", parent=styles["Normal"], fontName="Courier", fontSize=8)
    story.append(Preformatted(code[:3000] + ("\n... [truncated]" if len(code) > 3000 else ""), code_style))
    story.append(Spacer(1, 0.2 * inch))

    story.append(Paragraph("Static issues", styles["Heading2"]))
    if static_issues:
        data = [["Line", "Type", "Message"]] + [[str(i.get("line", "")), i.get("type", ""), (i.get("message", ""))[:60]] for i in static_issues[:30]]
        t = Table(data, colWidths=[1 * inch, 1.2 * inch, 3.5 * inch])
        t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.grey), ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke), ("FONTSIZE", (0, 0), (-1, -1), 8), ("GRID", (0, 0), (-1, -1), 0.5, colors.grey)]))
        story.append(t)
    else:
        story.append(Paragraph("None", styles["Normal"]))
    story.append(Spacer(1, 0.2 * inch))

    story.append(Paragraph("Time complexity reasoning", styles["Heading2"]))
    for r in time_reasons[:15]:
        story.append(Paragraph(f"Line {r.get('line', '')}: {r.get('reason', '')} → {r.get('contribution', '')}", styles["Normal"]))
    story.append(Spacer(1, 0.2 * inch))

    story.append(Paragraph("Space complexity reasoning", styles["Heading2"]))
    for r in space_reasons[:10]:
        story.append(Paragraph(f"{r.get('reason', '')} → {r.get('contribution', '')}", styles["Normal"]))
    story.append(Spacer(1, 0.2 * inch))

    if ai_explanation:
        story.append(Paragraph("AI explanation", styles["Heading2"]))
        story.append(Preformatted(ai_explanation[:2000], styles["Normal"]))
        story.append(Spacer(1, 0.2 * inch))
    if ai_bugs:
        story.append(Paragraph("AI bug / fix suggestions", styles["Heading2"]))
        story.append(Preformatted(ai_bugs[:1500], styles["Normal"]))

    doc.build(story)
    buf.seek(0)
    return buf
