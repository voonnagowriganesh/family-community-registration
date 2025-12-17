from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime
import os
import uuid

def generate_pdf(data: dict, language: str = "en") -> str:
    file_name = f"{uuid.uuid4()}.pdf"
    output_dir = os.path.join("media", "pdfs")
    os.makedirs(output_dir, exist_ok=True)

    file_path = os.path.join(output_dir, file_name)

    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    y = height - 50

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Community Registration Submission")
    y -= 30

    c.setFont("Helvetica", 10)
    c.drawString(50, y, f"Submitted On: {datetime.now().strftime('%d-%m-%Y %H:%M')}")
    y -= 30

    fields = [
        ("Full Name", data.get("full_name")),
        ("Surname", data.get("surname")),
        ("Desired Name", data.get("desired_name")),
        ("Father / Husband Name", data.get("father_or_husband_name")),
        ("Mother Name", data.get("mother_name")),
        ("Gothram", data.get("gothram")),
        ("Education", data.get("education")),
        ("Occupation", data.get("occupation")),
        ("Village / City", data.get("village_city")),
        ("Mandal", data.get("mandal")),
        ("District", data.get("district")),
        ("State", data.get("state")),
        ("PIN Code", data.get("pin_code")),
        ("Status", "Pending Approval"),
    ]

    for label, value in fields:
        if value:
            c.drawString(50, y, f"{label}: {value}")
            y -= 20

        if y < 100:
            c.showPage()
            c.setFont("Helvetica", 10)
            y = height - 50

    c.showPage()
    c.save()

    return file_path
