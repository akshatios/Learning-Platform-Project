from motor.motor_asyncio import AsyncIOMotorClient as MongoClient
from core.config import MONGODB_URL, DB_NAME
from core.redis_client import connect_redis_sync, close_redis_sync

# Create a MongoDB client
client = MongoClient(MONGODB_URL)

# Access the default database
db = client.get_database(DB_NAME)

# Define collections
users_collection = db.users  # Temporarily using users until data is moved
courses_collection = db.courses
course_videos_collection = db.course_videos

async def connect_to_mongo():
    connect_redis_sync()
    print("Connected to MongoDB")

async def close_mongo_connection():
    close_redis_sync()
    client.close()
    print("Disconnected from MongoDB")

def get_database():
    return db

