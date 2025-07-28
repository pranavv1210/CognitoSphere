# backend/database.py

from motor.motor_asyncio import AsyncMongoClient # NEW IMPORT
from dotenv import load_dotenv
import os

load_dotenv() # Load environment variables

MONGO_DB_URL = os.getenv("MONGO_DB_URL", "mongodb://localhost:27017/")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "cognitosphere_db")

class MongoManager:
    client: AsyncMongoClient = None # Changed type hint
    db = None

    async def connect_to_db(self):
        try:
            self.client = AsyncMongoClient(MONGO_DB_URL) # Changed MongoClient to AsyncMongoClient
            # The 'await' is crucial here for the connection if it's genuinely async operation,
            # though motor's client init is often sync for connection params then async for ops.
            await self.client.admin.command('ping') # Test connection with an async ping
            self.db = self.client[MONGO_DB_NAME]
            print(f"Connected to MongoDB: {MONGO_DB_URL}, Database: {MONGO_DB_NAME}")
        except Exception as e:
            print(f"Failed to connect to MongoDB: {e}")
            self.client = None
            self.db = None

    async def close_db_connection(self):
        if self.client:
            self.client.close()
            print("MongoDB connection closed.")

mongo_manager = MongoManager()