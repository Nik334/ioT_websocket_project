from motor.motor_asyncio import AsyncIOMotorClient

from app.config import settings

client: AsyncIOMotorClient | None = None
db = None


async def connect_to_mongo():
    global client, db
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]

    await db.iot_data.create_index("user_id")
    await db.iot_data.create_index("timestamp")
    await db.iot_data.create_index([("user_id", 1), ("timestamp", -1)])


async def close_mongo_connection():
    global client, db
    if client:
        client.close()
    client = None
    db = None


def get_database():
    return db
