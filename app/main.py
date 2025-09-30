from fastapi import FastAPI
from app.utils.email_utils import send_alert_email
from app.utils.openai_utils import get_openai_usage
import os
from datetime import datetime


app = FastAPI()


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # load from env

def send_usage_alert():
    try:
        report = get_openai_usage(OPENAI_API_KEY)

        subject = "🔔 OpenAI API Credit Usage Alert"
        body = f"""
        ✅ OpenAI API Usage Report ({datetime.utcnow().date()})

        - Today's usage: ${report['today_usage']:.2f}
        - Monthly usage: ${report['monthly_usage']:.2f}
        - Plan limit: ${report['total_limit']:.2f}
        - Remaining balance: ${report['remaining_balance']:.2f}

        ⚠️ Keep an eye on usage to avoid service interruptions.
        """

        send_email(subject, body)

    except Exception as e:
        send_email("🚨 API Usage Monitor Error", f"Error while fetching usage: {str(e)}")

@app.get("/")
def root():
    return {"message": "API Credit Monitor Running"}

@app.get("/test-email")
def test_email():
    send_alert_email("Test Alert", "This is a test email from API Credit Monitor.")
    return {"status": "Email function executed"}