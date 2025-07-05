import smtplib
import os
from email.message import EmailMessage

def send_reset_email(to_email: str, reset_link: str):
    msg = EmailMessage()
    msg["Subject"] = "Password Reset Request"
    msg["From"] = os.environ.get("SES_FROM_EMAIL", "no-reply@example.com")
    msg["To"] = to_email
    msg.set_content(f"Click the link to reset your password: {reset_link}")

    SMTP_HOST = os.environ.get("SES_SMTP_HOST", "email-smtp.us-east-1.amazonaws.com")
    SMTP_PORT = int(os.environ.get("SES_SMTP_PORT", 587))
    SMTP_USER = os.environ.get("SES_SMTP_USER")
    SMTP_PASS = os.environ.get("SES_SMTP_PASS")

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
    except Exception as e:
        print(f"Failed to send email: {e}") 