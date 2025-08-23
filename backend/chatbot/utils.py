import random
import base64
import qrcode
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from datetime import datetime


def generate_ticket_number() -> str:
    """Generate a unique ATB ticket number."""
    return f"ATB-{random.randint(1000, 9999)}"


def generate_qr_code(ticket_number: str) -> tuple[str, BytesIO]:
    """
    Generate a QR code with a link to the ticket page.
    """
    url = f"http://localhost:8000/ticket/{ticket_number}"  # Replace localhost in production

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return img_base64, buffer



def generate_ticket_pdf(ticket_data: dict) -> BytesIO:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    c.setFont("Helvetica-Bold", 18)
    c.drawString(100, 780, f"🎟️ TICKET N° {ticket_data['ticket_number']}")

    c.setFont("Helvetica", 14)
    c.drawString(100, 750, f"Date: {ticket_data.get('date')}")
    c.drawString(100, 730, f"Heure: {ticket_data.get('time')}")
    c.drawString(100, 710, f"Service: {ticket_data.get('service')}")
    c.drawString(100, 690, f"Agence: {ticket_data.get('location')}")
    c.drawString(100, 670, f"Client ID: {ticket_data.get('user')}")

    qr_base64 = ticket_data.get('ticket_qr_base64')
    if qr_base64:
        qr_buffer = BytesIO(base64.b64decode(qr_base64))
        qr_image = ImageReader(qr_buffer)
        c.drawImage(qr_image, 100, 500, width=150, height=150)

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer
