from app.utils.database import users_collection
import asyncio

async def setup_dummy_user():
    await users_collection.update_one(
        {"email": "aashiraqeel2@gmail.com"},
        {"$set": {"remaining_credits": 3, "last_usage_value": 10}},  # below threshold
        upsert=True
    )
    print("✅ Dummy user is ready!")

asyncio.run(setup_dummy_user())
