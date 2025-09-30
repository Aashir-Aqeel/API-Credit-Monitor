import os
import requests
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from app.models.api_record import UsageRecord
from app.utils.email_utils import send_email

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGO_URL)
db = client["credit_monitor"]
usage_collection = db["usage_records"]

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_URL = "https://api.openai.com/v1/organization/usage/costs"

import os
from datetime import datetime, timedelta
import httpx  # async http client
from app.utils.email_utils import send_email_alert
from app.models.usage_record import UsageRecord
from app.database import usage_collection

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_URL = os.getenv("OPENAI_API_URL", "https://api.openai.com/v1/usage")

async def fetch_and_store_usage():
    today = datetime.utcnow().date()
    yesterday = today - timedelta(days=1)

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
    }

    params = {
        "start_date": str(yesterday),
        "end_date": str(yesterday),
        "granularity": "daily",
    }

    # ✅ async request
    async with httpx.AsyncClient() as client:
        response = await client.get(OPENAI_API_URL, headers=headers, params=params)
        data = response.json()

    daily_costs = data.get("daily_costs", {})
    total_cost = data.get("total_cost", 0.0)

    # ✅ fetch last record
    last_record = await usage_collection.find_one(sort=[("date", -1)])
    balance_before = last_record["balance_after"] if last_record else float(os.getenv("MONTHLY_CREDIT", "100.0"))
    balance_after = balance_before - total_cost

    alerted = False
    if balance_after < 30:
        alerted = True
        send_email_alert(
            subject="⚠️ Low Credit Alert",
            body=f"Your remaining balance is ${balance_after:.2f}. Please recharge soon!"
        )

    record = UsageRecord(
        project_id="openai",
        date=datetime.utcnow(),
        daily_costs=daily_costs,
        total_cost=total_cost,
        balance_before=balance_before,
        balance_after=balance_after,
        alerted=alerted,
    )

    await usage_collection.insert_one(record.dict())
    print(f"📊 Stored usage record for {yesterday}: ${total_cost:.2f} spent, balance left ${balance_after:.2f}")
