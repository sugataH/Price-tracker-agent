# backend/app/alerts/email_alert.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))

async def send_email_alert(to_email: str, product_name: str, product_url: str, old_price: float, new_price: float, near: bool = False):
    """
    Send an HTML email alert. This function is synchronous (smtplib) but marked async for caller compatibility.
    It's safe to call with 'await'.
    """
    if not to_email:
        print("  ⚠ send_email_alert called without to_email")
        return

    subject = f"🔔 Price Alert — {product_name}"
    if near:
        subject = f"⚠️ {product_name} price near historical low"
    else:
        subject = f"🔥 {product_name} new lowest price!"

    body = f"""
    <html><body>
      <h2>{subject}</h2>
      <p><b>Old Price:</b> ₹{old_price if old_price is not None else 'N/A'}</p>
      <p><b>New Price:</b> <span style="color:green; font-weight:bold;">₹{new_price if new_price is not None else 'N/A'}</span></p>
      <p><a href="{product_url}" target="_blank">Open product link</a></p>
      <hr/>
      <p style="font-size:12px;color:#666;">This alert was sent by your AI Price Tracker Agent.</p>
    </body></html>
    """

    msg = MIMEMultipart()
    msg["From"] = SMTP_EMAIL or "no-reply@example.com"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as server:
            server.starttls()
            if SMTP_EMAIL and SMTP_PASSWORD:
                server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.sendmail(msg["From"], [to_email], msg.as_string())
        print(f"  📧 Email sent to {to_email}")
    except Exception as e:
        print(f"  ❌ Failed to send email to {to_email}: {e}")
