from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.config import settings 
import requests
import resend 
import base64
import os

resend.api_key = settings.resend_api_key

# utils/mail/user_vr_darshan_mails.py
import resend

async def send_user_approval_mail(b):
    resend.Emails.send({
        "from": "Tirth Ghumo <no-reply@tirthghumo.in>",
        "to": [b.email_address],
        "subject": "🙏 Your VR Darshan is Confirmed",
        "text": f"""
Hello 😊,

We’re happy to let you know that your **VR Darshan booking has been confirmed** 🙏🌼

On "{b.preferred_date}" at "{b.time_slot}", our "Saarthi will come to your place" to help you experience the darshan in a calm and comfortable way.  
Before coming, **our Saarthi will call you** to inform and coordinate with you .

Please don’t worry about anything 🤍  
Our Saarthi will handle the setup and gently guide you, so you can sit peacefully and enjoy the darshan 🕊️

If you ever need to **change the date or time**, that’s completely okay 😊  
Just **send us a message on {6260499299} at least 24 hours before**. We’re always happy to help 🌸

We hope this darshan brings peace to your heart and a gentle smile to your face 😊🌷  
Thank you for trusting us 🤍

With warm wishes,  
Team TirthGhumo 🌼

"""
    })


async def send_user_decline_age_mail(b):
    resend.Emails.send({
        "from": "Tirth Ghumo <no-reply@tirthghumo.in>",
        "to": [b.email_address],
        "subject": "🙏 Regarding Your VR Darshan Booking",
        "text": """
Hello 😊,

Thank you so much for your interest in VR Darshan and for sharing your details with us 🙏  
We truly appreciate the trust you have shown in TirthGhumo 🌸

After carefully checking the information, we noticed that the **age mentioned in the ID proof does not match the age entered in the form**.  
Because of this, we are unable to proceed with the booking at this moment .

If you would like to **update or correct the details**, you are most. welcome to contact us directly on this number {6260499299}  
We will be happy to guide you and help you with the next steps 😊

Thank you once again for your understanding and patience 🌼  
We truly hope to serve you soon and be part of your spiritual journey 🙏✨

With warm regards,  
**Team TirthGhumo** 🌸
"""
    })


async def send_user_decline_payment_mail(b):
    resend.Emails.send({
        "from": "Tirth Ghumo <no-reply@tirthghumo.in>",
        "to": [b.email_address],
        "subject": "🙏 Regarding Your VR Darshan Booking",
        "text": """
Hello 😊,

Thank you so much for your interest in VR Darshan and for sharing your details with us 🙏  
We truly appreciate the trust you have shown in TirthGhumo 🌸.

We wanted to let you know that we've reviewed your recent booking attempt.
Unfortunately, we couldn’t verify the payment details on our end.

This might be due to a mismatch in the transaction ID or some other discrepancy.

If you believe this is an error, please feel free to reach out to us at
{6260499299} — we’ll be happy to help resolve the issue.

We appreciate your understanding and hope to welcome you on another adventure soon.

Warm regards,
Team TirthGhumo
"""
    })
