"""
Career Analysis Report PDF Generator
Creates a professional, well-formatted PDF report of the career analysis.
Uses ReportLab with custom styling for a polished look.
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
    Table, TableStyle, ListFlowable, ListItem, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.utils import simpleSplit
from reportlab.graphics.shapes import Drawing, Rect, String, Circle, Wedge, Line
from reportlab.graphics import renderPDF
from xml.sax.saxutils import escape as xml_escape
from io import BytesIO
from datetime import datetime
from typing import Dict, Any, List
import math


def _safe(text: str) -> str:
    """Escape text for safe use in ReportLab Paragraph XML."""
    if not text:
        return ""
    return xml_escape(str(text))


# ── Color Palette ──────────────────────────────────────────────
NAVY = colors.HexColor('#1e293b')
DARK_BLUE = colors.HexColor('#1e3a5f')
PRIMARY = colors.HexColor('#6366f1')
PRIMARY_DARK = colors.HexColor('#4f46e5')
PRIMARY_LIGHT = colors.HexColor('#e0e7ff')
ACCENT = colors.HexColor('#8b5cf6')
EMERALD = colors.HexColor('#059669')
EMERALD_LIGHT = colors.HexColor('#d1fae5')
AMBER = colors.HexColor('#d97706')
AMBER_LIGHT = colors.HexColor('#fef3c7')
RED = colors.HexColor('#dc2626')
RED_LIGHT = colors.HexColor('#fee2e2')
GRAY_700 = colors.HexColor('#374151')
GRAY_500 = colors.HexColor('#6b7280')
GRAY_400 = colors.HexColor('#9ca3af')
GRAY_300 = colors.HexColor('#d1d5db')
GRAY_200 = colors.HexColor('#e5e7eb')
GRAY_100 = colors.HexColor('#f3f4f6')
GRAY_50 = colors.HexColor('#f9fafb')
WHITE = colors.HexColor('#ffffff')


def _build_styles():
    """Create all the custom paragraph styles for the report."""
    styles = getSampleStyleSheet()
    
    custom = {}
    
    custom['title'] = ParagraphStyle(
        'ReportTitle',
        parent=styles['Heading1'],
        fontSize=26,
        textColor=WHITE,
        spaceAfter=2,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        leading=32,
    )
    
    custom['subtitle'] = ParagraphStyle(
        'ReportSubtitle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#c7d2fe'),
        spaceAfter=4,
        alignment=TA_CENTER,
        fontName='Helvetica',
    )
    
    custom['date'] = ParagraphStyle(
        'ReportDate',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#a5b4fc'),
        spaceAfter=0,
        alignment=TA_CENTER,
        fontName='Helvetica',
    )
    
    custom['section_heading'] = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=13,
        textColor=PRIMARY_DARK,
        spaceBefore=16,
        spaceAfter=8,
        fontName='Helvetica-Bold',
        leading=17,
        borderWidth=0,
        borderPadding=0,
    )
    
    custom['subsection'] = ParagraphStyle(
        'SubSection',
        parent=styles['Heading3'],
        fontSize=10,
        textColor=GRAY_700,
        spaceBefore=10,
        spaceAfter=4,
        fontName='Helvetica-Bold',
        leading=13,
    )
    
    custom['body'] = ParagraphStyle(
        'ReportBody',
        parent=styles['Normal'],
        fontSize=9.5,
        textColor=GRAY_700,
        spaceAfter=6,
        alignment=TA_LEFT,
        leading=14,
        fontName='Helvetica',
    )
    
    custom['body_bold'] = ParagraphStyle(
        'ReportBodyBold',
        parent=styles['Normal'],
        fontSize=9.5,
        textColor=NAVY,
        spaceAfter=4,
        fontName='Helvetica-Bold',
        leading=14,
    )
    
    custom['bullet'] = ParagraphStyle(
        'BulletItem',
        parent=styles['Normal'],
        fontSize=9.5,
        textColor=GRAY_700,
        spaceAfter=3,
        leftIndent=12,
        fontName='Helvetica',
        leading=14,
    )
    
    custom['strength_bullet'] = ParagraphStyle(
        'StrengthBullet',
        parent=styles['Normal'],
        fontSize=9.5,
        textColor=GRAY_700,
        spaceAfter=4,
        leftIndent=12,
        fontName='Helvetica',
        leading=14,
    )
    
    custom['score_big'] = ParagraphStyle(
        'ScoreBig',
        parent=styles['Normal'],
        fontSize=36,
        textColor=PRIMARY,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        spaceAfter=4,
    )
    
    custom['score_label'] = ParagraphStyle(
        'ScoreLabel',
        parent=styles['Normal'],
        fontSize=10,
        textColor=GRAY_500,
        alignment=TA_CENTER,
        fontName='Helvetica',
        spaceAfter=6,
    )
    
    custom['footer'] = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=7.5,
        textColor=GRAY_400,
        alignment=TA_CENTER,
        fontName='Helvetica',
    )
    
    custom['roadmap_title'] = ParagraphStyle(
        'RoadmapTitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=NAVY,
        spaceAfter=1,
        fontName='Helvetica-Bold',
        leading=13,
    )
    
    custom['roadmap_detail'] = ParagraphStyle(
        'RoadmapDetail',
        parent=styles['Normal'],
        fontSize=8.5,
        textColor=GRAY_500,
        spaceAfter=6,
        leftIndent=12,
        fontName='Helvetica',
        leading=11,
    )
    
    custom['tag'] = ParagraphStyle(
        'Tag',
        parent=styles['Normal'],
        fontSize=8,
        textColor=PRIMARY,
        fontName='Helvetica-Bold',
    )
    
    return custom


def _create_header_banner(width):
    """Create a colored header banner drawing."""
    d = Drawing(width, 108)
    
    # Main gradient-like banner (solid since ReportLab doesn't support gradients)
    d.add(Rect(0, 0, width, 108, fillColor=colors.HexColor('#4f46e5'),
               strokeColor=None, rx=0, ry=0))
    
    # Accent overlay bar at top
    d.add(Rect(0, 98, width, 10, fillColor=colors.HexColor('#4338ca'),
               strokeColor=None))
    
    # Accent overlay bar at bottom
    d.add(Rect(0, 0, width, 3, fillColor=colors.HexColor('#6366f1'),
               strokeColor=None))
    
    # Title text
    d.add(String(width / 2, 68, "Career Copilot AI",
                 fontSize=24, fontName='Helvetica-Bold',
                 fillColor=WHITE, textAnchor='middle'))
    
    # Subtitle
    d.add(String(width / 2, 48, "Career Analysis Report",
                 fontSize=11, fontName='Helvetica',
                 fillColor=colors.HexColor('#c7d2fe'), textAnchor='middle'))
    
    # Date
    date_str = datetime.now().strftime('%B %d, %Y at %I:%M %p')
    d.add(String(width / 2, 30, f"Generated on {date_str}",
                 fontSize=8, fontName='Helvetica',
                 fillColor=colors.HexColor('#a5b4fc'), textAnchor='middle'))
    
    # Decorative dots
    for x_pos in [30, width - 30]:
        d.add(Circle(x_pos, 78, 3, fillColor=colors.HexColor('#818cf8'),
                     strokeColor=None))
        d.add(Circle(x_pos, 40, 2, fillColor=colors.HexColor('#6366f1'),
                     strokeColor=None))
    
    return d


def _create_score_visual(score, width):
    """Create a visual score display with arc and number."""
    d = Drawing(width, 100)
    center_x = width / 2
    center_y = 50
    radius = 38
    
    score_color = _get_score_color(score)
    
    # Background circle (track)
    d.add(Circle(center_x, center_y, radius,
                 fillColor=GRAY_100, strokeColor=GRAY_200, strokeWidth=1))
    
    # Inner circle (white)
    d.add(Circle(center_x, center_y, radius - 8,
                 fillColor=WHITE, strokeColor=None))
    
    # Score arc (colored ring segment)
    angle = (score / 100) * 360
    if angle > 0:
        d.add(Wedge(center_x, center_y, radius - 1, 90, 90 - angle,
                     fillColor=score_color, strokeColor=None))
        # Re-draw inner white to make it a ring
        d.add(Circle(center_x, center_y, radius - 8,
                     fillColor=WHITE, strokeColor=None))
    
    # Score text
    d.add(String(center_x, center_y + 3, f"{score}%",
                 fontSize=22, fontName='Helvetica-Bold',
                 fillColor=score_color, textAnchor='middle'))
    
    # Verdict text
    if score >= 75:
        verdict = "Excellent Match"
    elif score >= 50:
        verdict = "Good Potential"
    else:
        verdict = "Needs Development"
    
    d.add(String(center_x, center_y - 14, verdict,
                 fontSize=7.5, fontName='Helvetica',
                 fillColor=GRAY_500, textAnchor='middle'))
    
    return d


def _create_section_header(text, color=PRIMARY_DARK):
    """Create a section heading with a colored left accent bar."""
    d = Drawing(6, 14)
    d.add(Rect(0, 0, 4, 14, fillColor=color, strokeColor=None, rx=2, ry=2))
    return d


def _add_section_divider(story):
    """Add a subtle section divider."""
    story.append(Spacer(1, 4))
    story.append(HRFlowable(
        width="100%", thickness=0.5, color=GRAY_200,
        spaceBefore=2, spaceAfter=8
    ))


def _get_score_color(score: int):
    """Return the appropriate color for a score value."""
    if score >= 75:
        return EMERALD
    elif score >= 50:
        return AMBER
    else:
        return RED


def _get_score_bg(score: int):
    """Return the appropriate light background for a score value."""
    if score >= 75:
        return EMERALD_LIGHT
    elif score >= 50:
        return AMBER_LIGHT
    else:
        return RED_LIGHT


def _add_page_number(canvas, doc):
    """Add page number and subtle footer to each page."""
    page_num = canvas.getPageNumber()
    text = f"Page {page_num}"
    canvas.saveState()
    canvas.setFont('Helvetica', 7)
    canvas.setFillColor(GRAY_400)
    canvas.drawRightString(doc.pagesize[0] - 0.75 * inch, 0.5 * inch, text)
    
    # Subtle bottom line
    canvas.setStrokeColor(GRAY_200)
    canvas.setLineWidth(0.5)
    canvas.line(0.75 * inch, 0.6 * inch,
                doc.pagesize[0] - 0.75 * inch, 0.6 * inch)
    canvas.restoreState()


def create_analysis_report(analysis: Dict[str, Any], resume_preview: Dict[str, Any] = None) -> bytes:
    """
    Generate a professional PDF career analysis report.
    
    Args:
        analysis: The full analysis dict from run_agent + enrichments
        resume_preview: Optional resume preview data
        
    Returns:
        PDF file as bytes
    """
    buffer = BytesIO()
    
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.75 * inch,
    )
    
    s = _build_styles()
    story = []
    
    target_role = analysis.get("target_role", "Target Role")
    score = analysis.get("role_fit_score", 0)
    page_width = doc.width
    
    # ── Header Banner ──────────────────────────────────────────────
    story.append(_create_header_banner(page_width))
    story.append(Spacer(1, 16))
    
    # ── Target Role Badge ──────────────────────────────────────────
    role_style = ParagraphStyle(
        'RoleBadge', fontSize=11, textColor=PRIMARY_DARK,
        alignment=TA_CENTER, fontName='Helvetica-Bold', leading=14,
    )
    role_table = Table(
        [[Paragraph(f"Target Role:  {_safe(target_role)}", role_style)]],
        colWidths=[page_width * 0.7],
    )
    role_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BACKGROUND', (0, 0), (0, 0), PRIMARY_LIGHT),
        ('ROUNDEDCORNERS', [6, 6, 6, 6]),
        ('TOPPADDING', (0, 0), (0, 0), 8),
        ('BOTTOMPADDING', (0, 0), (0, 0), 8),
        ('LEFTPADDING', (0, 0), (0, 0), 16),
        ('RIGHTPADDING', (0, 0), (0, 0), 16),
    ]))
    wrapper = Table([[role_table]], colWidths=[page_width])
    wrapper.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER')]))
    story.append(wrapper)
    story.append(Spacer(1, 12))
    
    # ── Resume Summary (if available) ───────────────────────────
    if resume_preview and resume_preview.get("detected_name"):
        # Info as a subtle card
        info_data = []
        if resume_preview.get("detected_name"):
            info_data.append([
                Paragraph("<b>Candidate</b>", s['body']),
                Paragraph(_safe(resume_preview["detected_name"]), s['body_bold'])
            ])
        if resume_preview.get("email"):
            info_data.append([
                Paragraph("<b>Email</b>", s['body']),
                Paragraph(_safe(resume_preview["email"]), s['body'])
            ])
        if resume_preview.get("page_count"):
            info_data.append([
                Paragraph("<b>Resume</b>", s['body']),
                Paragraph(
                    f"{resume_preview['page_count']} page(s), "
                    f"{resume_preview.get('word_count', 0)} words", s['body'])
            ])
        
        if info_data:
            info_table = Table(info_data, colWidths=[1.2 * inch, page_width - 1.2 * inch])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), GRAY_50),
                ('ROUNDEDCORNERS', [6, 6, 6, 6]),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('LINEBELOW', (0, 0), (-1, -2), 0.5, GRAY_200),
            ]))
            story.append(info_table)
            story.append(Spacer(1, 6))
        
        # Skills detected
        if resume_preview.get("skills_detected"):
            skills_text = "  |  ".join(resume_preview["skills_detected"])
            story.append(Paragraph(
                f'<font color="#6366f1"><b>Skills Detected:</b></font>  {_safe(skills_text)}',
                s['body']
            ))
        
        story.append(Spacer(1, 8))
    
    # ── Role Fit Score ──────────────────────────────────────────
    _add_section_divider(story)
    story.append(Paragraph(
        '<font color="#4f46e5">ROLE FIT SCORE</font>',
        s['section_heading']
    ))
    
    # Score visual
    score_drawing = _create_score_visual(score, page_width)
    story.append(score_drawing)
    
    # Analysis notes
    notes = analysis.get("analysis_notes", "")
    if notes:
        # Put notes in a light card
        notes_table = Table(
            [[Paragraph(_safe(notes), s['body'])]],
            colWidths=[page_width - 20],
        )
        notes_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), GRAY_50),
            ('ROUNDEDCORNERS', [4, 4, 4, 4]),
            ('TOPPADDING', (0, 0), (0, 0), 8),
            ('BOTTOMPADDING', (0, 0), (0, 0), 8),
            ('LEFTPADDING', (0, 0), (0, 0), 10),
            ('RIGHTPADDING', (0, 0), (0, 0), 10),
        ]))
        wrapper = Table([[notes_table]], colWidths=[page_width])
        wrapper.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER')]))
        story.append(Spacer(1, 6))
        story.append(wrapper)
    
    # ── Strengths ───────────────────────────────────────────────
    strengths = analysis.get("strengths", [])
    if strengths:
        _add_section_divider(story)
        story.append(Paragraph(
            '<font color="#059669">KEY STRENGTHS</font>',
            s['section_heading']
        ))
        for strength in strengths:
            story.append(Paragraph(
                f'<font color="#059669"><b>+</b></font>  {_safe(strength)}',
                s['strength_bullet']
            ))
    
    # ── Skill Gaps ──────────────────────────────────────────────
    skill_gaps = analysis.get("skill_gaps", {})
    core_gaps = skill_gaps.get("core", [])
    supporting_gaps = skill_gaps.get("supporting", [])
    
    if core_gaps or supporting_gaps:
        _add_section_divider(story)
        story.append(Paragraph(
            '<font color="#dc2626">SKILL GAPS TO ADDRESS</font>',
            s['section_heading']
        ))
        
        if core_gaps:
            story.append(Paragraph(
                '<font color="#dc2626"><b>Core Skills Needed</b></font>',
                s['subsection']
            ))
            for gap in core_gaps:
                story.append(Paragraph(
                    f'<font color="#dc2626"><b>-</b></font>  {_safe(gap)}',
                    s['bullet']
                ))
        
        if supporting_gaps:
            story.append(Paragraph(
                '<font color="#d97706"><b>Supporting Skills</b></font>',
                s['subsection']
            ))
            for gap in supporting_gaps:
                story.append(Paragraph(
                    f'<font color="#d97706"><b>-</b></font>  {_safe(gap)}',
                    s['bullet']
                ))
    
    # ── Learning Roadmap ────────────────────────────────────────
    roadmap = analysis.get("roadmap", [])
    if roadmap:
        _add_section_divider(story)
        story.append(Paragraph(
            '<font color="#4f46e5">PERSONALIZED LEARNING ROADMAP</font>',
            s['section_heading']
        ))
        
        for i, item in enumerate(roadmap, 1):
            if isinstance(item, dict):
                skill_name = _safe(item.get("skill", item.get("name", f"Step {i}")))
                resource = item.get("resource", item.get("resources", ""))
                timeline = item.get("timeline", item.get("duration", ""))
                priority = item.get("priority", "")
                outcome = item.get("expected_outcome", item.get("outcome", ""))
                
                # Step number badge + name
                p_color = _priority_hex(priority) if priority else "6366f1"
                step_text = f'<font color="#{p_color}"><b>Step {i}</b></font>  {skill_name}'
                if priority:
                    step_text += f'  <font color="#{p_color}" size="8">({priority})</font>'
                
                # Wrap in a subtle card
                card_content = [[Paragraph(step_text, s['roadmap_title'])]]
                
                # Details line
                details = []
                if timeline:
                    details.append(f"Timeline: {_safe(timeline)}")
                if resource:
                    if isinstance(resource, list):
                        details.append(f"Resources: {_safe(', '.join(resource))}")
                    else:
                        details.append(f"Resources: {_safe(resource)}")
                if outcome:
                    details.append(f"Goal: {_safe(outcome)}")
                
                if details:
                    card_content.append([Paragraph(
                        "  |  ".join(details), s['roadmap_detail']
                    )])
                
                card_table = Table(card_content, colWidths=[page_width - 24])
                card_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), GRAY_50),
                    ('ROUNDEDCORNERS', [4, 4, 4, 4]),
                    ('TOPPADDING', (0, 0), (0, 0), 6),
                    ('BOTTOMPADDING', (0, -1), (0, -1), 6),
                    ('LEFTPADDING', (0, 0), (-1, -1), 10),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                    ('LINEBELOW', (0, 0), (0, 0), 0, WHITE),
                ]))
                story.append(card_table)
                story.append(Spacer(1, 4))
            else:
                # Simple string item
                story.append(Paragraph(
                    f'<font color="#6366f1"><b>Step {i}</b></font>  {_safe(item)}',
                    s['roadmap_title']
                ))
                story.append(Spacer(1, 4))
    
    # ── AI Reflection ───────────────────────────────────────────
    reflection = analysis.get("reflection", {})
    if reflection:
        _add_section_divider(story)
        story.append(Paragraph(
            '<font color="#8b5cf6">AI AGENT REFLECTION</font>',
            s['section_heading']
        ))
        
        if isinstance(reflection, dict):
            summary = reflection.get("summary", "")
            reason = reflection.get("reason", "")
            confidence = reflection.get("confidence", "")
            suggestions = reflection.get("suggestions", [])
            status = reflection.get("status", "")
            
            display_text = summary or reason or ""
            if display_text:
                # Card style
                refl_table = Table(
                    [[Paragraph(_safe(display_text), s['body'])]],
                    colWidths=[page_width - 20],
                )
                refl_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f5f3ff')),
                    ('ROUNDEDCORNERS', [4, 4, 4, 4]),
                    ('TOPPADDING', (0, 0), (0, 0), 8),
                    ('BOTTOMPADDING', (0, 0), (0, 0), 8),
                    ('LEFTPADDING', (0, 0), (0, 0), 10),
                    ('RIGHTPADDING', (0, 0), (0, 0), 10),
                ]))
                wrapper2 = Table([[refl_table]], colWidths=[page_width])
                wrapper2.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER')]))
                story.append(wrapper2)
            
            if confidence:
                story.append(Spacer(1, 4))
                story.append(Paragraph(
                    f'<font color="#8b5cf6"><b>Confidence:</b></font>  {_safe(confidence)}',
                    s['body']
                ))
            
            if status:
                story.append(Paragraph(
                    f'<font color="#8b5cf6"><b>Status:</b></font>  {_safe(status)}',
                    s['body']
                ))
            
            if suggestions:
                story.append(Spacer(1, 4))
                story.append(Paragraph(
                    '<font color="#8b5cf6"><b>Additional Suggestions:</b></font>',
                    s['subsection']
                ))
                for sug in suggestions:
                    story.append(Paragraph(
                        f'<font color="#8b5cf6">*</font>  {_safe(sug)}',
                        s['bullet']
                    ))
        elif isinstance(reflection, str):
            story.append(Paragraph(_safe(reflection), s['body']))
    
    # ── Footer ──────────────────────────────────────────────────
    story.append(Spacer(1, 24))
    _add_section_divider(story)
    story.append(Paragraph(
        "Generated by Career Copilot AI  |  "
        "This report is AI-generated and should be used as guidance, not as a definitive assessment.",
        s['footer']
    ))
    
    # Build PDF with page numbers
    doc.build(story, onFirstPage=_add_page_number, onLaterPages=_add_page_number)
    pdf_content = buffer.getvalue()
    buffer.close()
    
    return pdf_content


def _priority_hex(priority: str) -> str:
    """Return a hex color string for a priority level."""
    p = priority.lower()
    if "high" in p or "critical" in p:
        return "dc2626"
    elif "medium" in p:
        return "d97706"
    else:
        return "059669"


def get_report_filename(target_role: str) -> str:
    """Generate a clean filename for the analysis report PDF."""
    clean_role = "".join(c if c.isalnum() or c == ' ' else '' for c in target_role)
    clean_role = clean_role.replace(' ', '_')[:30]
    timestamp = datetime.now().strftime("%Y%m%d")
    return f"Career_Analysis_{clean_role}_{timestamp}.pdf"
