from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = "mydatabase"

client = AsyncIOMotorClient(MONGO_URI)
database = client[DATABASE_NAME]
items_collection = database.get_collection("items")