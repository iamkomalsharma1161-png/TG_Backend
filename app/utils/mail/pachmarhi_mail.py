from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from fastapi import Depends 
from app.config import settings 
from sqlalchemy.orm import Session
from sqlalchemy.orm import Session
from app.database import engine , get_db
from app import models 
import requests
import resend 
import base64
import os

resend.api_key = settings.resend_api_key
base_url = settings.base_url


def send_booking_email(
    booking_id: int ,  
    db:Session,
    image_path: str | None = None  ):
    booking = db.query(models.Pachmarhi).filter(
        models.Pachmarhi.id == booking_id
    ).first()

    travellers = db.query(models.PachmarhiTraveller).filter(
        models.PachmarhiTraveller.booking_id == booking_id
    ).all()

    traveller_html = ""

    for i, t in enumerate(travellers, 1):
        traveller_html += f"""
        <p>{i}. {t.full_name} | {t.age} | {t.gender}</p>
        """
    admin_action_base = "https://tgbackend-production-bd64.up.railway.app/pachmarhi/approve"
    approve_link = f"{admin_action_base}?booking_id={booking_id}"
    decline_link = f"https://tgbackend-production-bd64.up.railway.app/pachmarhi/decline?booking_id={booking_id}"
    html_body = f"""
    <h2>New Trek Booking</h2>

    <p><b>Booking ID:</b> {booking.id}</p>
    <p><b>Primary Email:</b> {booking.primary_email}</p>
    <p><b>Total People:</b> {booking.total_people}</p>
    <p><b>Total Amount:</b> ₹{booking.total_price}</p>
    <p><b>Meal:</b> {booking.meal_preference}</p>
    <p><b>Sharing:</b> {booking.sharing_preference}</p>
    <p><b>Payment Option:</b> {booking.payment_option}</p>

    <h3>Travellers</h3>
    {traveller_html}

    <a href="{approve_link}">Approve</a>
    <br><br>
    <a href="{decline_link}">Decline</a>
    """
    attachments = []

    if image_path and os.path.exists(image_path):
        with open(image_path, "rb") as f:
            file_data = base64.b64encode(f.read()).decode("utf-8")
            file_name = os.path.basename(image_path)
            attachments.append({
                "content": file_data,
                "filename": file_name,
                "type": "image/jpeg" if image_path.lower().endswith((".jpg", ".jpeg")) else "image/png"
            })

    email_payload = {
        "from": "Tirth Ghumo <no-reply@tirthghumo.in>",
        "to":"thekomal2502@gmail.com",
        "subject":"New Trek Booking Verification",
        "html": html_body
    }
    if attachments:
            email_payload["attachments"] = attachments

    response = resend.Emails.send(email_payload)
    print("EMAIL SENT SUCCESSFULLY:", response)

async def send_booking_declined_email(data , email):
    try:
        text_body = f"""
        Hello,

Thank you for choosing TirthGhumo for your adventure.
We wanted to let you know that we've reviewed your recent booking attempt.
Unfortunately, we couldn’t verify the payment details on our end.

This might be due to a mismatch in the transaction ID or some other discrepancy.

If you believe this is an error, please feel free to reach out to us at
6260499299 / 6204289831 — we’ll be happy to help resolve the issue.

We appreciate your understanding and hope to welcome you on another adventure soon.

Warm regards,
Team TirthGhumo
        """.strip()

        email_payload = {
            "from": "Tirth Ghumo <no-reply@tirthghumo.in>",
            "to": [email],
            "subject": "Booking Update – Action Required",
            "text": text_body,
        }

        resend.Emails.send(email_payload)

    except Exception as e:
        print("DECLINE EMAIL ERROR:", e)
        raise




async def send_email_with_invoice(email ,data, invoice_path):
    """Send invoice PDF to user using Resend"""

    # ---- Attach PDF ----
    with open(invoice_path, "rb") as f:
        file_bytes = base64.b64encode(f.read()).decode("utf-8")

    # ---- Email Body ----
    email_body = f"""
   Hey🌿

Thank you so much for booking with us! We are truly honoured to be a part of your journey.

Your booking for the Pachmarhi trip has been received successfully. We are so excited for you and we promise to make this an experience you will always remember.

Our team will reach out to you soon with all the details. Until then, sit back and start getting excited for an amazing adventure!

Wishing you a wonderful trip ahead. 🌿

Warm regards,
Team TirthGhumo

Thank you for choosing TirthGhumo — Aastha Bhi, Suvidha Bhi 🌄

    """

    # ---- Email Payload ----
    email_payload = {
        "from": "Tirth Ghumo <no-reply@tirthghumo.in>",
        "to": [email],
        "subject": "Booking Confirmed – See You in Pachmarhi! 🌿",
        "text": email_body.strip(),
        "attachments": [
            {
                "filename": "invoice.pdf",
                "content": file_bytes,
                "type": "application/pdf"
            }
        ]
    }

    # ---- Send ----
    try:
        resend.Emails.send(email_payload)
    except Exception as e:
        raise Exception(f"Invoice email failed: {str(e)}")
