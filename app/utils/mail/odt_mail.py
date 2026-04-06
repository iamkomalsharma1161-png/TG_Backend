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
conf = ConnectionConfig(
    MAIL_USERNAME= settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_STARTTLS=settings.mail_starttls,
    MAIL_SSL_TLS=settings.mail_ssl_tls,
    USE_CREDENTIALS=settings.use_credentials,
)

resend.api_key = settings.resend_api_key
base_url = settings.base_url



def send_booking_email(
    booking_id: int ,  
    db:Session,
    image_path: str | None = None  ):
    booking = db.query(models.ODT1).filter(
        models.ODT1.id == booking_id
    ).first()

    travellers = db.query(models.ODTTraveller).filter(
        models.ODTTraveller.booking_id == booking_id
    ).all()

    traveller_html = ""

    for i, t in enumerate(travellers, 1):
        traveller_html += f"""
        <p>{i}. {t.full_name} | {t.age} | {t.gender}</p>
        """
    admin_action_base = "https://tgbackend-production-bd64.up.railway.app/odt/approve"
    approve_link = f"{admin_action_base}?booking_id={booking_id}"
    decline_link = f"https://tgbackend-production-bd64.up.railway.app/odt/decline?booking_id={booking_id}"
    html_body = f"""
    <h2>New Trek Booking</h2>

    <p><b>Booking ID:</b> {booking.id}</p>
    <p><b>Primary Email:</b> {booking.primary_email}</p>
    <p><b>Total People:</b> {booking.total_people}</p>
    <p><b>Total Amount:</b> ₹{booking.total_price}</p>
    <p><b>Meal:</b> {booking.meal_preference}</p>

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
        "to":"tirthghumo@gmail.com",
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

Great news — your booking for the 1Day Mrignnath Trek with TirthGhumo 
is confirmed for 12th April 2026!

Your payment has been approved successfully . 

All essential trip details, including timings and instructions, 
will be shared shortly on WhatsApp.

Please make sure you’ve requested to join the WhatsApp group,
as all updates will be shared there.

If you need any help or have questions, feel free to contact us 
at 6260499299 / 6204289831.

Get ready for an exciting adventure and a day full of unforgettable memories!

Warm regards,
Team TirthGhumo

Thank you for choosing TirthGhumo — Aastha Bhi, Suvidha Bhi 🌄

    """

    # ---- Email Payload ----
    email_payload = {
        "from": "Tirth Ghumo <no-reply@tirthghumo.in>",
        "to": [email],
        "subject": "Your Trek Booking Invoice",
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




# async def send_booking_email(data , image_path: str | None = None):
#     try:
#         admin_action_base = "https://tgbackend-production-bd64.up.railway.app/odt/confirm"
    
#         button_1251 = f"{admin_action_base}?booking_id={data.id}&amount=1251"
#         button_1101 = f"{admin_action_base}?booking_id={data.id}&amount=1101"
#         button_1351= f"{admin_action_base}?booking_id={data.id}&amount=1351"
#         button_1201 = f"{admin_action_base}?booking_id={data.id}&amount=1201"
#         decline_link = f"https://tgbackend-production-bd64.up.railway.app/odt/decline?booking_id={data.id}"

#         safe_text = f"""
#         A new trekking booking has been submitted.
#         Student Details:
#         Name: {data.full_name}
#         Email: {data.email_address}
#         Contact: {data.contact_number}
#         College: {data.college_name}
#         Package Review Links:
#         • Without Meal (1201): {button_1201}
#         • With Meal(1351): {button_1351}
#         • Coupon and with meal(1251): {button_1251}
#         • Coupon and without meal(1101): {button_1101}
        
#         Decline booking: {decline_link}

        
#             """

#         attachments = []

#         if image_path and os.path.exists(image_path):
#             with open(image_path, "rb") as f:
#                 file_data = base64.b64encode(f.read()).decode("utf-8")
#                 file_name = os.path.basename(image_path)
#                 attachments.append({
#                     "content": file_data,
#                     "filename": file_name,
#                     "type": "image/jpeg" if image_path.lower().endswith((".jpg", ".jpeg")) else "image/png"
#                 })

#         email_payload = {
#             "from": "Tirth Ghumo <no-reply@tirthghumo.in>",
#             "to": ["tirthghumo@gmail.com"],
#             "subject": "New Trekking Package Booking",
#             "text": safe_text.strip(),
#                 } 


#         if attachments:
#             email_payload["attachments"] = attachments

#         response = resend.Emails.send(email_payload)
#         print("EMAIL SENT SUCCESSFULLY:", response)

#     except Exception as e:
#         print("EMAIL ERROR:", e)
#         raise

# async def send_booking_declined_email(data):
#     try:
#         text_body = f"""
#         Hey {data.full_name},

# Thank you for choosing TirthGhumo for your adventure.
# We wanted to let you know that we've reviewed your recent booking attempt.
# Unfortunately, we couldn’t verify the payment details on our end.

# This might be due to a mismatch in the transaction ID or some other discrepancy.

# If you believe this is an error, please feel free to reach out to us at
# 6260499299 / 6204289831 — we’ll be happy to help resolve the issue.

# We appreciate your understanding and hope to welcome you on another adventure soon.

# Warm regards,
# Team TirthGhumo
#         """.strip()

#         email_payload = {
#             "from": "Tirth Ghumo <no-reply@tirthghumo.in>",
#             "to": [data.email_address],
#             "subject": "Booking Update – Action Required",
#             "text": text_body,
#         }

#         resend.Emails.send(email_payload)

#     except Exception as e:
#         print("DECLINE EMAIL ERROR:", e)
#         raise




# async def send_email_with_invoice(data, invoice_path):
#     """Send invoice PDF to user using Resend"""

#     # ---- Attach PDF ----
#     with open(invoice_path, "rb") as f:
#         file_bytes = base64.b64encode(f.read()).decode("utf-8")

#     # ---- Email Body ----
#     email_body = f"""
#    Hey {data.full_name} 🌿

# Great news — your booking for the 1Day Mrignnath Trek with TirthGhumo 
# is confirmed for 12th April 2026!

# Your payment has been approved successfully . 

# All essential trip details, including timings and instructions, 
# will be shared shortly on WhatsApp.

# Please make sure you’ve requested to join the WhatsApp group,
# as all updates will be shared there.

# If you need any help or have questions, feel free to contact us 
# at 6260499299 / 6204289831.

# Get ready for an exciting adventure and a day full of unforgettable memories!

# Warm regards,
# Team TirthGhumo

# Thank you for choosing TirthGhumo — Aastha Bhi, Suvidha Bhi 🌄

#     """

#     # ---- Email Payload ----
#     email = {
#         "from": "Tirth Ghumo <no-reply@tirthghumo.in>",
#         "to": [data.email_address],
#         "subject": "Your Trek Booking Invoice",
#         "text": email_body.strip(),
#         "attachments": [
#             {
#                 "filename": "invoice.pdf",
#                 "content": file_bytes,
#                 "type": "application/pdf"
#             }
#         ]
#     }

#     # ---- Send ----
#     try:
#         resend.Emails.send(email)
#     except Exception as e:
#         raise Exception(f"Invoice email failed: {str(e)}")

##############ODT CHANGES ################

