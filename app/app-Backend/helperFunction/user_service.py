from core.database import get_database
from core.redis_client import set_user_online, set_user_offline, is_user_online, get_online_users_count
from bson import ObjectId

db = get_database()

async def user_login(user_id: str):
    """Handle user login - set online in Redis and update DB"""
    # Set user online in Redis
    await set_user_online(user_id)
    
    # Update isActive to True in database
    await db.Users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"isActive": True}}
    )

async def user_logout(user_id: str):
    """Handle user logout - remove from Redis and update DB"""
    # Set user offline in Redis
    await set_user_offline(user_id)
    
    # Update isActive to False in database
    await db.Users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"isActive": False}}
    )

async def get_user_status(user_id: str):
    """Get user online status from Redis"""
    return await is_user_online(user_id)

async def get_active_users_stats():
    """Get statistics of active users"""
    online_count = await get_online_users_count()
    
    # Get total users from database
    total_users = await db.Users.count_documents({})
    
    # Get offline count
    offline_count = total_users - online_count
    
    return {
        "total_users": total_users,
        "online_users": online_count,
        "offline_users": offline_count
    }