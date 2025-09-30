import os
import requests
import logging
from app.utils.database import users_collection
from app.utils.email_utils import send_email

# Configure logger for monitor
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

async def check_user_credits():
    results = []
    users_cursor = users_collection.find({})
    
    async for user in users_cursor:
        email = user.get("email", "N/A")
        remaining_credits = float(user.get("remaining_credits", 0))
        last_value = float(user.get("last_usage_value", 0))
        last_start_time = int(user.get("last_start_time", 0))
        
        logger.info(f"Checking user: {email}")
        logger.info(f"Current remaining_credits: {remaining_credits}, last_value: {last_value}, last_start_time: {last_start_time}")

        # Fetch latest OpenAI usage
        url = f"https://api.openai.com/v1/organization/costs?start_time={last_start_time}&limit=1"
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
        try:
            resp = requests.get(url, headers=headers)
            data = resp.json()
        except Exception as e:
            logger.error(f"Failed to fetch OpenAI usage for {email}: {e}")
            continue

        delta = 0
        if "data" in data and len(data["data"]) > 0:
            bucket = data["data"][0]
            results_list = bucket.get("results", [])
            if results_list:
                current_value = float(results_list[0]["amount"]["value"])
                delta = current_value - last_value
                if delta != 0:
                    remaining_credits -= delta
                    await users_collection.update_one(
                        {"_id": user["_id"]},
                        {"$set": {"last_usage_value": current_value, "remaining_credits": remaining_credits}}
                    )
                    logger.info(f"Updated remaining_credits for {email} by delta: {delta:.2f}. New balance: {remaining_credits:.2f}")
                else:
                    logger.info(f"No change in usage for {email}. Delta: {delta:.2f}")

        # Send alert email if below threshold
        if remaining_credits <= ALERT_THRESHOLD:
            await send_email(
                to_email=email,
                subject="⚠️ Low OpenAI Credits Alert",
                body=f"Your remaining OpenAI credits are ${remaining_credits:.2f}"
            )
            logger.info(f"⚠️ Alert email sent to {email}. Remaining credits: {remaining_credits:.2f}")
        else:
            logger.info(f"No alert email sent for {email}. Remaining credits: {remaining_credits:.2f}")

        results.append({
            "user": email,
            "remaining_credits": remaining_credits,
            "delta": delta
        })

    return results
