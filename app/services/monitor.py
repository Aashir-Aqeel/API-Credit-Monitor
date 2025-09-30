# app/monitor.py

import os
import requests
import logging
from datetime import datetime
from app.utils.database import remaining_balance_collection, email_address_collection
from app.utils.email_utils import send_email

# Configure logger
logger = logging.getLogger("monitor")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.FileHandler("credit_monitor.log")
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.addHandler(logging.StreamHandler())

ALERT_THRESHOLD = int(os.getenv("ALERT_THRESHOLD", 4))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


async def run_monitor():
    """
    Wrapper for the scheduler — checks user credits.
    """
    await check_user_credits()


async def check_user_credits():
    """
    Checks remaining balance, updates it from OpenAI API, 
    and sends alert email if under threshold.
    """
    try:
        balance_doc = await remaining_balance_collection.find_one()
        if not balance_doc:
            logger.warning("No balance record found.")
            return

        remaining_credits = float(balance_doc.get("remaining_credits", 0))
        last_value = float(balance_doc.get("last_usage_value", 0))
        last_start_time = int(balance_doc.get("last_start_time", 0))

        logger.info(
            f"Current remaining_credits: {remaining_credits}, "
            f"last_value: {last_value}, last_start_time: {last_start_time}"
        )

        # Fetch usage from OpenAI API
        url = f"https://api.openai.com/v1/organization/costs?start_time={last_start_time}&limit=1"
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
        try:
            resp = requests.get(url, headers=headers)
            data = resp.json()
        except Exception as e:
            logger.error(f"Failed to fetch OpenAI usage: {e}")
            return

        delta = 0
        if "data" in data and len(data["data"]) > 0:
            bucket = data["data"][0]
            results_list = bucket.get("results", [])
            if results_list:
                current_value = float(results_list[0]["amount"]["value"])
                delta = current_value - last_value
                if delta != 0:
                    remaining_credits -= delta
                    await remaining_balance_collection.update_one(
                        {"_id": balance_doc["_id"]},
                        {"$set": {
                            "last_usage_value": current_value,
                            "remaining_credits": remaining_credits,
                            "last_checked": datetime.utcnow()
                        }}
                    )
                    logger.info(
                        f"Updated remaining_credits by delta {delta:.2f}. "
                        f"New balance: {remaining_credits:.2f}"
                    )
                else:
                    logger.info(f"No change in usage. Delta: {delta:.2f}")

        # Check threshold
        if remaining_credits <= ALERT_THRESHOLD:
            await notify_alerts(remaining_credits)
        else:
            logger.info(
                f"Balance is healthy. No alerts. Remaining credits: {remaining_credits:.2f}"
            )

    except Exception as e:
        logger.error(f"Error in check_user_credits: {e}")


async def notify_alerts(remaining_credits: float):
    """
    Sends alert emails to all addresses in email_address collection.
    """
    try:
        recipients = await email_address_collection.find().to_list(length=100)
        if not recipients:
            logger.warning("No alert email addresses found.")
            return

        for r in recipients:
            email = r.get("email")
            if email:
                await send_email(
                    to_email=email,
                    subject="⚠️ Low OpenAI Credits Alert",
                    body=f"Your remaining OpenAI credits are ${remaining_credits:.2f}"
                )
                logger.info(
                    f"Alert email sent to {email}. "
                    f"Remaining credits: {remaining_credits:.2f}"
                )

    except Exception as e:
        logger.error(f"Error sending alert emails: {e}")
