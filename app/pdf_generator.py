"""
PDF Generator for Cover Letters
Uses ReportLab to create professional PDF cover letters
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from io import BytesIO
from datetime import datetime
from typing import Dict, Any


def create_cover_letter_pdf(cover_letter_data: Dict[str, Any]) -> bytes:
    """
    Generate a professional PDF cover letter.
    
    Args:
        cover_letter_data: Dict containing:
            - cover_letter: The main text
            - company: Company name
            - position: Job title
            - candidate_name: Applicant's name
            
    Returns:
        PDF file as bytes
    """
    
    # Create BytesIO buffer
    buffer = BytesIO()
    
    # Create PDF document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=1*inch,
        leftMargin=1*inch,
        topMargin=1*inch,
        bottomMargin=1*inch
    )
    
    # Create custom styles
    styles = getSampleStyleSheet()
    
    # Header style (candidate name)
    header_style = ParagraphStyle(
        'Header',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1e3a5f'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Date style
    date_style = ParagraphStyle(
        'Date',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#666666'),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    # Company info style
    company_style = ParagraphStyle(
        'Company',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#333333'),
        spaceAfter=4,
        alignment=TA_LEFT,
        fontName='Helvetica-Bold'
    )
    
    # Body paragraph style
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#333333'),
        spaceAfter=12,
        alignment=TA_JUSTIFY,
        leading=16,
        fontName='Helvetica'
    )
    
    # Signature style
    signature_style = ParagraphStyle(
        'Signature',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#333333'),
        spaceBefore=20,
        alignment=TA_LEFT,
        fontName='Helvetica'
    )
    
    # Build document content
    story = []
    
    # Candidate name header
    candidate_name = cover_letter_data.get('candidate_name', 'Applicant')
    story.append(Paragraph(candidate_name, header_style))
    
    # Current date
    current_date = datetime.now().strftime("%B %d, %Y")
    story.append(Paragraph(current_date, date_style))
    
    # Horizontal line
    story.append(HRFlowable(
        width="100%",
        thickness=1,
        color=colors.HexColor('#1e3a5f'),
        spaceBefore=5,
        spaceAfter=20
    ))
    
    # Company and position
    company = cover_letter_data.get('company', 'Company')
    position = cover_letter_data.get('position', 'Position')
    story.append(Paragraph(f"RE: Application for {position}", company_style))
    story.append(Paragraph(f"at {company}", company_style))
    story.append(Spacer(1, 20))
    
    # Cover letter body
    cover_letter_text = cover_letter_data.get('cover_letter', '')
    
    # Split by paragraphs and add each
    paragraphs = cover_letter_text.split('\n\n')
    for para in paragraphs:
        if para.strip():
            # Clean up the text for PDF
            clean_para = para.replace('\n', ' ').strip()
            if clean_para:
                story.append(Paragraph(clean_para, body_style))
    
    # Add signature if not already in the letter
    if 'sincerely' not in cover_letter_text.lower():
        story.append(Spacer(1, 20))
        story.append(Paragraph("Sincerely,", signature_style))
        story.append(Spacer(1, 10))
        story.append(Paragraph(candidate_name, signature_style))
    
    # Build PDF
    doc.build(story)
    
    # Get PDF content
    pdf_content = buffer.getvalue()
    buffer.close()
    
    return pdf_content


def get_cover_letter_filename(company: str, position: str) -> str:
    """
    Generate a clean filename for the cover letter PDF.
    """
    # Clean company name
    clean_company = "".join(c if c.isalnum() or c == ' ' else '' for c in company)
    clean_company = clean_company.replace(' ', '_')[:20]
    
    # Clean position
    clean_position = "".join(c if c.isalnum() or c == ' ' else '' for c in position)
    clean_position = clean_position.replace(' ', '_')[:20]
    
    # Create filename
    timestamp = datetime.now().strftime("%Y%m%d")
    filename = f"Cover_Letter_{clean_company}_{clean_position}_{timestamp}.pdf"
    
    return filename
