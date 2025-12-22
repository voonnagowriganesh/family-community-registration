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
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics import renderPDF
from reportlab.graphics.charts.piecharts import Pie
from reportlab.platypus.flowables import KeepTogether

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
    
    # Style for HTML content in tables
    styles.add(ParagraphStyle(
        name='TableCell',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.black,
        leading=12
    ))
    
    styles.add(ParagraphStyle(
        name='BoldValue',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#1f2937'),
        fontName='Helvetica-Bold'
    ))
    
    # Title and Header
    elements.append(Paragraph("KANAGALA FAMILY COMMUNITY", styles['TitleStyle']))
    elements.append(Paragraph("Official Registration Certificate", styles['SubtitleStyle']))
    
    # Add decorative line
    elements.append(Spacer(1, 20))
    
    # Generate Registration ID
    registration_id = f"KGC-{uuid.uuid4().hex[:8].upper()}"
    
    # Registration Info Box - Using Paragraphs for HTML content
    reg_info_data = [
        [Paragraph("Registration ID:", styles['TableCell']), 
         Paragraph(registration_id, styles['BoldValue'])],
        [Paragraph("Submission Date:", styles['TableCell']), 
         Paragraph(datetime.now().strftime('%d %B, %Y'), styles['TableCell'])],
        [Paragraph("Submission Time:", styles['TableCell']), 
         Paragraph(datetime.now().strftime('%I:%M %p'), styles['TableCell'])],
        [Paragraph("Status:", styles['TableCell']), 
         Paragraph("<font color='green'><b>PENDING APPROVAL</b></font>", styles['TableCell'])]
    ]
    
    reg_table = Table(reg_info_data, colWidths=[2*inch, 3*inch])
    reg_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#dbeafe')),
        ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#f0f9ff')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
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
    
    # Format date if available
    dob = data.get("date_of_birth", "N/A")
    if dob != "N/A":
        try:
            dob_date = datetime.strptime(dob, '%Y-%m-%d')
            dob = dob_date.strftime('%d %B, %Y')
        except:
            pass
    
    # Create personal data with Paragraphs
    personal_data = []
    personal_data.append([
        Paragraph("Full Name:", styles['TableCell']), 
        Paragraph(data.get("full_name", "N/A"), styles['TableCell'])
    ])
    personal_data.append([
        Paragraph("Surname:", styles['TableCell']), 
        Paragraph(f"<b>{data.get('surname', 'N/A')}</b>", styles['TableCell'])
    ])
    personal_data.append([
        Paragraph("Desired Name:", styles['TableCell']), 
        Paragraph(data.get("desired_name", "N/A"), styles['TableCell'])
    ])
    personal_data.append([
        Paragraph("Father/Husband Name:", styles['TableCell']), 
        Paragraph(data.get("father_or_husband_name", "N/A"), styles['TableCell'])
    ])
    personal_data.append([
        Paragraph("Mother Name:", styles['TableCell']), 
        Paragraph(data.get("mother_name", "N/A"), styles['TableCell'])
    ])
    personal_data.append([
        Paragraph("Date of Birth:", styles['TableCell']), 
        Paragraph(dob, styles['TableCell'])
    ])
    personal_data.append([
        Paragraph("Gender:", styles['TableCell']), 
        Paragraph(data.get("gender", "N/A"), styles['TableCell'])
    ])
    personal_data.append([
        Paragraph("Blood Group:", styles['TableCell']), 
        Paragraph(f"<font color='red'><b>{data.get('blood_group', 'N/A')}</b></font>", styles['TableCell'])
    ])
    personal_data.append([
        Paragraph("Gothram:", styles['TableCell']), 
        Paragraph(data.get("gothram", "N/A"), styles['TableCell'])
    ])
    personal_data.append([
        Paragraph("Aaradhya Daiva:", styles['TableCell']), 
        Paragraph(data.get("aaradhya_daiva", "N/A") if data.get("aaradhya_daiva") else "Not Specified", styles['TableCell'])
    ])
    personal_data.append([
        Paragraph("Kula Devata:", styles['TableCell']), 
        Paragraph(data.get("kula_devata", "N/A") if data.get("kula_devata") else "Not Specified", styles['TableCell'])
    ])
    
    personal_table = Table(personal_data, colWidths=[2.5*inch, 4*inch])
    personal_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
        ('BACKGROUND', (1, 0), (1, -1), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
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
    
    edu_occ_data = []
    edu_occ_data.append([
        Paragraph("Education:", styles['TableCell']), 
        Paragraph(data.get("education", "N/A"), styles['TableCell'])
    ])
    edu_occ_data.append([
        Paragraph("Occupation:", styles['TableCell']), 
        Paragraph(data.get("occupation", "N/A"), styles['TableCell'])
    ])
    
    edu_occ_table = Table(edu_occ_data, colWidths=[2.5*inch, 4*inch])
    edu_occ_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#fef3c7')),
        ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#fffbeb')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
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
    
    address_data = []
    address_data.append([
        Paragraph("House Number:", styles['TableCell']), 
        Paragraph(data.get("house_number", "N/A") if data.get("house_number") else "Not Specified", styles['TableCell'])
    ])
    address_data.append([
        Paragraph("Village/City:", styles['TableCell']), 
        Paragraph(data.get("village_city", "N/A"), styles['TableCell'])
    ])
    address_data.append([
        Paragraph("Mandal:", styles['TableCell']), 
        Paragraph(data.get("mandal", "N/A") if data.get("mandal") else "Not Specified", styles['TableCell'])
    ])
    address_data.append([
        Paragraph("District:", styles['TableCell']), 
        Paragraph(data.get("district", "N/A"), styles['TableCell'])
    ])
    address_data.append([
        Paragraph("State:", styles['TableCell']), 
        Paragraph(data.get("state", "N/A"), styles['TableCell'])
    ])
    address_data.append([
        Paragraph("Country:", styles['TableCell']), 
        Paragraph(data.get("country", "N/A"), styles['TableCell'])
    ])
    address_data.append([
        Paragraph("PIN Code:", styles['TableCell']), 
        Paragraph(data.get("pin_code", "N/A"), styles['TableCell'])
    ])
    
    address_table = Table(address_data, colWidths=[2*inch, 4.5*inch])
    address_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#dcfce7')),
        ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#f0fdf4')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
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
    
    contact_data = []
    contact_data.append([
        Paragraph("Email:", styles['TableCell']), 
        Paragraph(data.get("email", "N/A"), styles['TableCell'])
    ])
    contact_data.append([
        Paragraph("Mobile Number:", styles['TableCell']), 
        Paragraph(data.get("mobile_number", "N/A") if data.get("mobile_number") else "Not Provided", styles['TableCell'])
    ])
    contact_data.append([
        Paragraph("Referred By:", styles['TableCell']), 
        Paragraph(data.get("referred_by_name", "Not Specified"), styles['TableCell'])
    ])
    contact_data.append([
        Paragraph("Referrer Mobile:", styles['TableCell']), 
        Paragraph(data.get("referred_mobile", "N/A") if data.get("referred_mobile") else "Not Provided", styles['TableCell'])
    ])
    
    contact_table = Table(contact_data, colWidths=[2*inch, 4.5*inch])
    contact_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#fae8ff')),
        ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#fdf4ff')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e879f9')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#c026d3')),
    ]))
    
    elements.append(contact_table)
    elements.append(Spacer(1, 30))
    
    # Feedback Section
    feedback = data.get("feedback")
    if feedback and feedback.strip():
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
        elements.append(Paragraph(f"\"{feedback}\"", feedback_style))
    
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
    
    # Add QR Code section (optional - requires qrcode library)
    try:
        # Create QR code with registration ID
        qr = qrcode.QRCode(version=1, box_size=4, border=2)
        qr_data = f"Registration ID: {registration_id}\nName: {data.get('full_name', 'N/A')}\nDate: {datetime.now().strftime('%Y-%m-%d')}"
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Create QR code image
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Save QR code to bytes
        qr_bytes = BytesIO()
        qr_img.save(qr_bytes, format='PNG')
        qr_bytes.seek(0)
        
        # Add QR code to PDF
        from reportlab.platypus import Image
        elements.append(Spacer(1, 20))
        qr_paragraph = Paragraph("<b>Scan QR for Verification</b>", ParagraphStyle(
            name='QRTitle',
            parent=styles['Normal'],
            fontSize=9,
            alignment=TA_CENTER
        ))
        elements.append(qr_paragraph)
        
        # Add the image
        qr_image = Image(qr_bytes, width=1.5*inch, height=1.5*inch)
        elements.append(qr_image)
        
    except ImportError:
        # QR code library not available, skip it
        pass
    
    # Build PDF
    doc.build(elements)
    
    # Return public URL
    return f"{BASE_URL}/media/pdfs/{file_name}"


# For backward compatibility
generate_pdf = generate_attractive_pdf