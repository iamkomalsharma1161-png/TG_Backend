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
    admin_action_base = base_url 
    approve_link = f"{admin_action_base}/pachmarhi/approve?booking_id={booking_id}"
    decline_link = f"{admin_action_base}/pachmarhi/decline?booking_id={booking_id}"
    html_body = f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background-color:#f4f4f4;font-family:Arial,sans-serif;">

  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f4f4;padding:30px 0;">
    <tr>
      <td align="center">
        <table width="620" cellpadding="0" cellspacing="0" style="background-color:#ffffff;border-radius:10px;overflow:hidden;">

          <!-- HEADER -->
          <tr>
            <td style="background-color:#1a1a2e;padding:24px 32px;text-align:center;">
              <h1 style="color:#ffffff;margin:0;font-size:22px;">🏔️ Tirth Ghumo</h1>
              <p style="color:#aaaacc;margin:4px 0 0;font-size:13px;">New Booking Received</p>
              <span style="display:inline-block;background-color:#f0a500;color:#1a1a2e;font-weight:bold;font-size:12px;padding:4px 12px;border-radius:20px;margin-top:10px;">Pachmarhi Trip</span>
            </td>
          </tr>

          <!-- BOOKING DETAILS -->
          <tr>
            <td style="padding:28px 32px;">
              <p style="font-size:13px;font-weight:bold;text-transform:uppercase;color:#888888;letter-spacing:1px;border-bottom:1px solid #eeeeee;padding-bottom:6px;margin-bottom:16px;">Booking Details</p>

              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td width="50%" style="padding:6px 8px 6px 0;">
                    <table width="100%" cellpadding="12" cellspacing="0" style="background-color:#f9f9f9;border-radius:8px;">
                      <tr>
                        <td>
                          <p style="font-size:11px;color:#999999;text-transform:uppercase;margin:0 0 4px;">Booking ID</p>
                          <p style="font-size:15px;font-weight:bold;color:#1a1a2e;margin:0;">#{booking.id}</p>
                        </td>
                      </tr>
                    </table>
                  </td>
                  <td width="50%" style="padding:6px 0 6px 8px;">
                    <table width="100%" cellpadding="12" cellspacing="0" style="background-color:#f9f9f9;border-radius:8px;">
                      <tr>
                        <td>
                          <p style="font-size:11px;color:#999999;text-transform:uppercase;margin:0 0 4px;">Primary Email</p>
                          <p style="font-size:15px;font-weight:bold;color:#1a1a2e;margin:0;">{booking.primary_email}</p>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
                <tr>
                  <td width="50%" style="padding:6px 8px 6px 0;">
                    <table width="100%" cellpadding="12" cellspacing="0" style="background-color:#f9f9f9;border-radius:8px;">
                      <tr>
                        <td>
                          <p style="font-size:11px;color:#999999;text-transform:uppercase;margin:0 0 4px;">Total Travellers</p>
                          <p style="font-size:15px;font-weight:bold;color:#1a1a2e;margin:0;">{booking.total_people}</p>
                        </td>
                      </tr>
                    </table>
                  </td>
                  <td width="50%" style="padding:6px 0 6px 8px;">
                    <table width="100%" cellpadding="12" cellspacing="0" style="background-color:#f9f9f9;border-radius:8px;">
                      <tr>
                        <td>
                          <p style="font-size:11px;color:#999999;text-transform:uppercase;margin:0 0 4px;">Total Amount</p>
                          <p style="font-size:15px;font-weight:bold;color:#1a1a2e;margin:0;">₹{booking.total_price}</p>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
                <tr>
                  <td width="50%" style="padding:6px 8px 6px 0;">
                    <table width="100%" cellpadding="12" cellspacing="0" style="background-color:#f9f9f9;border-radius:8px;">
                      <tr>
                        <td>
                          <p style="font-size:11px;color:#999999;text-transform:uppercase;margin:0 0 4px;">Meal Preference</p>
                          <p style="font-size:15px;font-weight:bold;color:#1a1a2e;margin:0;">{booking.meal_preference.replace("_", " ").title()}</p>
                        </td>
                      </tr>
                    </table>
                  </td>
                  <td width="50%" style="padding:6px 0 6px 8px;">
                    <table width="100%" cellpadding="12" cellspacing="0" style="background-color:#f9f9f9;border-radius:8px;">
                      <tr>
                        <td>
                          <p style="font-size:11px;color:#999999;text-transform:uppercase;margin:0 0 4px;">Sharing Preference</p>
                          <p style="font-size:15px;font-weight:bold;color:#1a1a2e;margin:0;">{booking.sharing_preference.title()}</p>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
                <tr>
                  <td width="50%" style="padding:6px 8px 6px 0;">
                    <table width="100%" cellpadding="12" cellspacing="0" style="background-color:#f9f9f9;border-radius:8px;">
                      <tr>
                        <td>
                          <p style="font-size:11px;color:#999999;text-transform:uppercase;margin:0 0 4px;">Payment Option</p>
                          <p style="font-size:15px;font-weight:bold;color:#1a1a2e;margin:0;">{booking.payment_option.title()}</p>
                        </td>
                      </tr>
                    </table>
                  </td>
                  <td width="50%" style="padding:6px 0 6px 8px;">
                    <table width="100%" cellpadding="12" cellspacing="0" style="background-color:#f9f9f9;border-radius:8px;">
                      <tr>
                        <td>
                          <p style="font-size:11px;color:#999999;text-transform:uppercase;margin:0 0 4px;">Booking Date</p>
                          <p style="font-size:15px;font-weight:bold;color:#1a1a2e;margin:0;">{str(booking.submitted_at.date()) if booking.submitted_at else "N/A"}</p>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- TRAVELLERS TABLE -->
          <tr>
            <td style="padding:0 32px 28px;">
              <p style="font-size:13px;font-weight:bold;text-transform:uppercase;color:#888888;letter-spacing:1px;border-bottom:1px solid #eeeeee;padding-bottom:6px;margin-bottom:16px;">Traveller Details</p>
              <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;font-size:14px;">
                <thead>
                  <tr>
                    <th style="background-color:#1a1a2e;color:#ffffff;padding:10px 14px;text-align:left;">#</th>
                    <th style="background-color:#1a1a2e;color:#ffffff;padding:10px 14px;text-align:left;">Name</th>
                    <th style="background-color:#1a1a2e;color:#ffffff;padding:10px 14px;text-align:left;">Age</th>
                    <th style="background-color:#1a1a2e;color:#ffffff;padding:10px 14px;text-align:left;">Gender</th>
                  </tr>
                </thead>
                <tbody>
                  {traveller_rows}
                </tbody>
              </table>
            </td>
          </tr>

          <!-- ACTION BUTTONS -->
          <tr>
            <td style="padding:0 32px 32px;text-align:center;">
              <p style="color:#666666;font-size:13px;margin-bottom:20px;">Please review the booking and take an action below.</p>
              <a href="{approve_link}" style="display:inline-block;padding:14px 40px;background-color:#28a745;color:#ffffff;text-decoration:none;border-radius:8px;font-size:15px;font-weight:bold;margin:0 10px;">✅ Approve</a>
              <a href="{decline_link}" style="display:inline-block;padding:14px 40px;background-color:#dc3545;color:#ffffff;text-decoration:none;border-radius:8px;font-size:15px;font-weight:bold;margin:0 10px;">❌ Decline</a>
            </td>
          </tr>

          <!-- FOOTER -->
          <tr>
            <td style="background-color:#f4f4f4;text-align:center;padding:16px;font-size:12px;color:#aaaaaa;">
              © 2026 Tirth Ghumo · This is an automated admin notification
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>

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
