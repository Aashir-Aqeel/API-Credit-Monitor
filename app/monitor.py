import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta, timezone
import requests
from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL")
TO_EMAIL = os.getenv("TO_EMAIL")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

# -------------------
# FUNCTION: Fetch usage
# -------------------
def fetch_openai_usage():
    now = datetime.now(timezone.utc)
    yesterday = now - timedelta(days=1)

    start_time = int(yesterday.timestamp())
    end_time = int(now.timestamp())

    url = f"https://api.openai.com/v1/organization/costs?start_time={start_time}&end_time={end_time}"

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    response = requests.get(url, headers=headers)
    data = response.json()

    total_amount = 0.0
    if "data" in data:
        for bucket in data["data"]:
            for result in bucket.get("results", []):
                total_amount += result["amount"]["value"]

    return total_amount, yesterday, now

# -------------------
# FUNCTION: Send email
# -------------------
def send_email(total_usage, start_time, end_time):
    msg = MIMEMultipart()
    msg['From'] = FROM_EMAIL
    msg['To'] = TO_EMAIL
    msg['Subject'] = "OpenAI API Daily Usage Report"

    body = f"""
Hello,

Here’s your OpenAI API usage for the last 24 hours:

📅 From: {start_time.strftime('%Y-%m-%d %H:%M UTC')}
📅 To:   {end_time.strftime('%Y-%m-%d %H:%M UTC')}

💰 Total Usage: ${total_usage:.2f} USD

Keep monitoring your usage to stay within budget.

Best,
Your API Usage Monitor
"""
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(FROM_EMAIL, SMTP_PASSWORD)
            server.send_message(msg)
        print(f"✅ Email sent successfully! Total usage: ${total_usage:.2f}")
    except Exception as e:
        print(f"❌ Email sending failed: {e}")


# -------------------
# FUNCTION: Monitor job
# -------------------
def monitor_job():
    total_usage, start_time, end_time = fetch_openai_usage()
    send_email(total_usage, start_time, end_time)

# -------------------
# SCHEDULER: Run every 24 hours
# -------------------
if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(monitor_job, 'interval', hours=24)
    print("⏱️ OpenAI API Monitor started. Sending daily usage email...")
    monitor_job()  # Run immediately on start
    scheduler.start()
