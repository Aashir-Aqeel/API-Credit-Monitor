import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://aqeelaashir6:KCwNBZZhEtwmnatL@cluster0.6uz7zar.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DB_NAME = os.getenv("DB_NAME", "credit_monitor")

# Connect to MongoDB
client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

# Collections
usage_collection = db["usage_records"]
api_collection = db["api_records"]
