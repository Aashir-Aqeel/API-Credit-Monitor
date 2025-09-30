import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os

# Load .env from the project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(BASE_DIR, ".env"))

def send_alert_email(subject: str, body: str):
    SMTP_HOST = os.getenv("SMTP_HOST")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER = os.getenv("SMTP_USER")
    SMTP_PASS = os.getenv("SMTP_PASS")
    FROM_EMAIL = os.getenv("FROM_EMAIL")
    ALERT_EMAIL = os.getenv("ALERT_EMAIL")

    if not all([SMTP_HOST, SMTP_USER, SMTP_PASS, FROM_EMAIL, ALERT_EMAIL]):
        print("❌ Email not sent: Missing SMTP configuration!")
        return

    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = FROM_EMAIL
        msg['To'] = ALERT_EMAIL

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(FROM_EMAIL, ALERT_EMAIL, msg.as_string())

        print("✅ Email sent successfully!")

    except Exception as e:
        print("❌ Email sending failed:", e)
