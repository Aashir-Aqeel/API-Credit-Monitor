# app/utils/database.py
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI") or "mongodb+srv://aqeelaashir6:KCwNBZZhEtwmnatL@cluster0.6uz7zar.mongodb.net/?retryWrites=true&w=majority"
DB_NAME = os.getenv("DB_NAME") or "credit_monitor"

# Async client
client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

# Collection
users_collection = db["users"]
