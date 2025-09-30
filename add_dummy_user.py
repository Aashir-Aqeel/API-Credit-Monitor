import asyncio
import time
from app.utils.database import db  # Make sure the path matches your project structure

async def add_dummy_user():
    users_collection = db["users"]
    dummy_user = {
        "email": "aashiraqeel2@gmail.com",   # Replace with your email
        "remaining_credits": 4,
        "last_usage_value": 10,
        "last_start_time": int(time.time())
    }

    # Insert the user
    await users_collection.insert_one(dummy_user)
    print("✅ Dummy user added successfully!")

# Run the async function
asyncio.run(add_dummy_user())
