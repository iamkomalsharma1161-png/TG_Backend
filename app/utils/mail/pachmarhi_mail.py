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
import httpx

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

    traveller_rows = ""
    for i, t in enumerate(travellers, 1):
        traveller_rows += f"""
        <tr>
            <td>{i}</td>
            <td>{t.full_name}</td>
            <td>{t.age}</td>
            <td>{t.gender.title()}</td>
        </tr>
        """
    admin_action_base = "https://tgbackend-production-bd64.up.railway.app/pachmarhi/approve"
    approve_link = f"{admin_action_base}?booking_id={booking_id}"
    decline_link = f"https://tgbackend-production-bd64.up.railway.app/pachmarhi/decline?booking_id={booking_id}"
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body {{
      font-family: Arial, sans-serif;
      background-color: #f4f4f4;
      margin: 0;
      padding: 0;
    }}
    .container {{
      max-width: 620px;
      margin: 30px auto;
      background-color: #ffffff;
      border-radius: 10px;
      overflow: hidden;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }}
    .header {{
      background-color: #1a1a2e;
      padding: 24px 32px;
      text-align: center;
    }}
    .header h1 {{
      color: #ffffff;
      margin: 0;
      font-size: 22px;
      letter-spacing: 1px;
    }}
    .header p {{
      color: #aaaacc;
      margin: 4px 0 0;
      font-size: 13px;
    }}
    .badge {{
      display: inline-block;
      background-color: #f0a500;
      color: #1a1a2e;
      font-weight: bold;
      font-size: 12px;
      padding: 4px 12px;
      border-radius: 20px;
      margin-top: 10px;
    }}
    .body {{
      padding: 28px 32px;
    }}
    .section-title {{
      font-size: 13px;
      font-weight: bold;
      text-transform: uppercase;
      color: #888888;
      letter-spacing: 1px;
      margin-bottom: 12px;
      border-bottom: 1px solid #eeeeee;
      padding-bottom: 6px;
    }}
    .info-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
      margin-bottom: 24px;
    }}
    .info-item {{
      background-color: #f9f9f9;
      border-radius: 8px;
      padding: 12px 16px;
    }}
    .info-item .label {{
      font-size: 11px;
      color: #999999;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 4px;
    }}
    .info-item .value {{
      font-size: 15px;
      font-weight: bold;
      color: #1a1a2e;
    }}
    .traveller-table {{
      width: 100%;
      border-collapse: collapse;
      margin-bottom: 24px;
      font-size: 14px;
    }}
    .traveller-table th {{
      background-color: #1a1a2e;
      color: #ffffff;
      padding: 10px 14px;
      text-align: left;
      font-weight: 600;
    }}
    .traveller-table td {{
      padding: 10px 14px;
      border-bottom: 1px solid #eeeeee;
      color: #333333;
    }}
    .traveller-table tr:last-child td {{
      border-bottom: none;
    }}
    .traveller-table tr:nth-child(even) td {{
      background-color: #f9f9f9;
    }}
    .action-section {{
      text-align: center;
      padding: 10px 0 10px;
    }}
    .action-section p {{
      color: #666666;
      font-size: 13px;
      margin-bottom: 20px;
    }}
    .btn {{
      display: inline-block;
      padding: 14px 40px;
      border-radius: 8px;
      font-size: 15px;
      font-weight: bold;
      text-decoration: none;
      margin: 0 10px;
      letter-spacing: 0.5px;
    }}
    .btn-approve {{
      background-color: #28a745;
      color: #ffffff;
    }}
    .btn-decline {{
      background-color: #dc3545;
      color: #ffffff;
    }}
    .footer {{
      background-color: #f4f4f4;
      text-align: center;
      padding: 16px;
      font-size: 12px;
      color: #aaaaaa;
    }}
  </style>
</head>
<body>
  <div class="container">

    <!-- HEADER -->
    <div class="header">
      <h1>🏔️ Tirth Ghumo</h1>
      <p>New Booking Received</p>
      <span class="badge">Pachmarhi Trip</span>
    </div>

    <!-- BODY -->
    <div class="body">

      <!-- BOOKING INFO -->
      <div class="section-title">Booking Details</div>
      <div class="info-grid">
        <div class="info-item">
          <div class="label">Booking ID</div>
          <div class="value">#{booking.id}</div>
        </div>
        <div class="info-item">
          <div class="label">Primary Email</div>
          <div class="value">{booking.primary_email}</div>
        </div>
        <div class="info-item">
          <div class="label">Total Travellers</div>
          <div class="value">{booking.total_people}</div>
        </div>
        <div class="info-item">
          <div class="label">Total Amount</div>
          <div class="value">₹{booking.total_price}</div>
        </div>
        <div class="info-item">
          <div class="label">Meal Preference</div>
          <div class="value">{booking.meal_preference.replace("_", " ").title()}</div>
        </div>
        <div class="info-item">
          <div class="label">Sharing Preference</div>
          <div class="value">{booking.sharing_preference.title()}</div>
        </div>
        <div class="info-item">
          <div class="label">Payment Option</div>
          <div class="value">{booking.payment_option.title()}</div>
        </div>
        <div class="info-item">
          <div class="label">Booking Date</div>
          <div class="value">{str(booking.submitted_at.date()) if booking.submitted_at else "N/A"}</div>
        </div>
      </div>

      <!-- TRAVELLERS TABLE -->
      <div class="section-title">Traveller Details</div>
      <table class="traveller-table">
        <thead>
          <tr>
            <th>#</th>
            <th>Name</th>
            <th>Age</th>
            <th>Gender</th>
          </tr>
        </thead>
        <tbody>
          {traveller_rows}
        </tbody>
      </table>

      <!-- ACTION BUTTONS -->
      <div class="action-section">
        <p>Please review the booking and take an action below.</p>
        <a href="{approve_link}" class="btn btn-approve">✅ Approve</a>
        <a href="{decline_link}" class="btn btn-decline">❌ Decline</a>
      </div>

    </div>

    <!-- FOOTER -->
    <div class="footer">
      © 2026 Tirth Ghumo · This is an automated admin notification
    </div>

  </div>
</body>
</html>
"""
    attachments = []

    if booking.payment_screenshot:
        try:
            response = httpx.get(booking.payment_screenshot)
            if response.status_code == 200:
                screenshot_base64 = base64.b64encode(response.content).decode("utf-8")
                content_type = response.headers.get("content-type", "image/jpeg")
                ext = content_type.split("/")[-1]  # jpg, png etc

                attachments.append({
                    "filename": f"payment_screenshot_{booking_id}.{ext}",
                    "content": screenshot_base64,
                    "type": content_type
                })
        except Exception as e:
            print("Failed to attach payment screenshot:", e)

    email_payload = {
        "from": "Tirth Ghumo <no-reply@tirthghumo.in>",
        "to":"thekomal2502@gmail.com",
        "subject":"New Pachmarhi Booking Verification",
        "html": html_body,
        "attachments": attachments
    }
    

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
