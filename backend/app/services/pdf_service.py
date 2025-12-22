from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
from datetime import datetime
import os
import uuid
import qrcode
from io import BytesIO
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics import renderPDF
from reportlab.graphics.charts.piecharts import Pie

BASE_URL = "https://family-community-registration-production.up.railway.app"

def generate_attractive_pdf(data: dict, language: str = "en") -> str:
    file_name = f"{uuid.uuid4()}.pdf"
    output_dir = os.path.join("media", "pdfs")
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, file_name)

    # Create document
    doc = SimpleDocTemplate(file_path, pagesize=A4,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=72)
    
    # Container for the 'Flowable' objects
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    styles.add(ParagraphStyle(
        name='TitleStyle',
        parent=styles['Title'],
        fontSize=24,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=30,
        alignment=TA_CENTER
    ))
    
    styles.add(ParagraphStyle(
        name='SubtitleStyle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#059669'),
        spaceAfter=20,
        alignment=TA_CENTER
    ))
    
    styles.add(ParagraphStyle(
        name='SectionHeader',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=12,
        spaceBefore=20,
        borderPadding=10,
        borderColor=colors.HexColor('#3b82f6'),
        borderWidth=1
    ))
    
    styles.add(ParagraphStyle(
        name='FieldLabel',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#4b5563'),
        spaceAfter=2
    ))
    
    styles.add(ParagraphStyle(
        name='FieldValue',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#1f2937'),
        spaceAfter=10,
        leftIndent=20
    ))
    
    # Title and Header
    elements.append(Paragraph("KANAGALA FAMILY COMMUNITY", styles['TitleStyle']))
    elements.append(Paragraph("Official Registration Certificate", styles['SubtitleStyle']))
    
    # Add decorative line
    elements.append(Spacer(1, 20))
    
    # Registration Info Box
    reg_info = [
        ["Registration ID:", f"KGC-{uuid.uuid4().hex[:8].upper()}"],
        ["Submission Date:", datetime.now().strftime('%d %B, %Y')],
        ["Submission Time:", datetime.now().strftime('%I:%M %p')],
        ["Status:", "<b><font color='green'>PENDING APPROVAL</font></b>"]
    ]
    
    reg_table = Table(reg_info, colWidths=[2*inch, 3*inch])
    reg_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#dbeafe')),
        ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#f0f9ff')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#93c5fd')),
        ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#1e3a8a')),
    ]))
    
    elements.append(reg_table)
    elements.append(Spacer(1, 30))
    
    # Personal Information Section
    elements.append(Paragraph("Personal Information", styles['SectionHeader']))
    
    personal_data = [
        ["Full Name:", data.get("full_name", "N/A")],
        ["Surname:", f"<b>{data.get('surname', 'N/A')}</b>"],
        ["Desired Name:", data.get("desired_name", "N/A")],
        ["Father/Husband Name:", data.get("father_or_husband_name", "N/A")],
        ["Mother Name:", data.get("mother_name", "N/A")],
        ["Date of Birth:", data.get("date_of_birth", "N/A")],
        ["Gender:", data.get("gender", "N/A")],
        ["Blood Group:", f"<font color='red'><b>{data.get('blood_group', 'N/A')}</b></font>"],
        ["Gothram:", data.get("gothram", "N/A")],
        ["Aaradhya Daiva:", data.get("aaradhya_daiva", "N/A")],
        ["Kula Devata:", data.get("kula_devata", "N/A")],
    ]
    
    personal_table = Table(personal_data, colWidths=[2.5*inch, 4*inch])
    personal_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
        ('BACKGROUND', (1, 0), (1, -1), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#9ca3af')),
    ]))
    
    elements.append(personal_table)
    elements.append(Spacer(1, 30))
    
    # Education & Occupation Section
    elements.append(Paragraph("Education & Occupation", styles['SectionHeader']))
    
    edu_occ_data = [
        ["Education:", data.get("education", "N/A")],
        ["Occupation:", data.get("occupation", "N/A")],
    ]
    
    edu_occ_table = Table(edu_occ_data, colWidths=[2.5*inch, 4*inch])
    edu_occ_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#fef3c7')),
        ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#fffbeb')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#fbbf24')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#f59e0b')),
    ]))
    
    elements.append(edu_occ_table)
    elements.append(Spacer(1, 30))
    
    # Address Information Section
    elements.append(Paragraph("Address Details", styles['SectionHeader']))
    
    address_data = [
        ["House Number:", data.get("house_number", "N/A")],
        ["Village/City:", data.get("village_city", "N/A")],
        ["Mandal:", data.get("mandal", "N/A")],
        ["District:", data.get("district", "N/A")],
        ["State:", data.get("state", "N/A")],
        ["Country:", data.get("country", "N/A")],
        ["PIN Code:", data.get("pin_code", "N/A")],
    ]
    
    address_table = Table(address_data, colWidths=[2*inch, 4.5*inch])
    address_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#dcfce7')),
        ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#f0fdf4')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#86efac')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#22c55e')),
    ]))
    
    elements.append(address_table)
    elements.append(Spacer(1, 30))
    
    # Contact Information Section
    elements.append(Paragraph("Contact Information", styles['SectionHeader']))
    
    contact_data = [
        ["Email:", data.get("email", "N/A")],
        ["Mobile Number:", data.get("mobile_number", "N/A")],
        ["Referred By:", data.get("referred_by_name", "Not Specified")],
        ["Referrer Mobile:", data.get("referred_mobile", "N/A")],
    ]
    
    contact_table = Table(contact_data, colWidths=[2*inch, 4.5*inch])
    contact_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#fae8ff')),
        ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#fdf4ff')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e879f9')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#c026d3')),
    ]))
    
    elements.append(contact_table)
    elements.append(Spacer(1, 30))
    
    # Feedback Section
    if data.get("feedback"):
        elements.append(Paragraph("Member Feedback", styles['SectionHeader']))
        feedback_style = ParagraphStyle(
            name='FeedbackStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#4b5563'),
            backColor=colors.HexColor('#f8fafc'),
            borderColor=colors.HexColor('#cbd5e1'),
            borderWidth=1,
            borderPadding=10,
            leftIndent=20,
            rightIndent=20,
            spaceAfter=20
        )
        elements.append(Paragraph(f"\"{data.get('feedback')}\"", feedback_style))
    
    # Footer Section with Important Notes
    elements.append(Spacer(1, 30))
    footer_style = ParagraphStyle(
        name='FooterStyle',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#6b7280'),
        alignment=TA_CENTER,
        spaceBefore=20
    )
    
    footer_text = """
    <b>IMPORTANT NOTES:</b><br/>
    1. This is a provisional registration certificate.<br/>
    2. Your registration will be verified by the community committee.<br/>
    3. Keep this certificate for future reference.<br/>
    4. Contact community office for any updates or changes.<br/>
    5. Registration ID must be quoted in all communications.<br/><br/>
    <i>© 2025 Kanagala Charitable Trust. All rights reserved.</i>
    """
    
    elements.append(Paragraph(footer_text, footer_style))
    
    # Build PDF
    doc.build(elements)
    
    # Return public URL
    return f"{BASE_URL}/media/pdfs/{file_name}"


# For backward compatibility
generate_pdf = generate_attractive_pdf