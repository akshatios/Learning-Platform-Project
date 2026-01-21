from motor.motor_asyncio import AsyncIOMotorClient as MongoClient
from core.config import settings

# Create a MongoDB client
client = MongoClient(settings.MONGODB_URL)

# Access the default database
db = client.get_database(settings.DB_NAME)

# Define collections
users_collection = db.users  # Temporarily using users until data is moved
admin_collection = db.admin
courses_collection = db.courses
course_videos_collection = db.course_videos

async def connect_to_mongo():
    print("Connected to MongoDB")

async def close_mongo_connection():
    client.close()
    print("Disconnected from MongoDB")

def get_database():
    return db