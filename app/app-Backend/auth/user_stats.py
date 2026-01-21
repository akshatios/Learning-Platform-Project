from fastapi import APIRouter, HTTPException
from pymongo import MongoClient
from bson import ObjectId
from core.config import MONGODB_URL, DB_NAME

router = APIRouter()

@router.get('/users/stats')
def get_users_stats():
    """Get total, online, and offline users count with details"""
    try:
        # Get online users from Redis
        from core.redis_client import get_online_users_count_sync, get_all_online_users_sync
        
        redis_online_count = get_online_users_count_sync()
        redis_online_user_ids = get_all_online_users_sync()
        
        client = MongoClient(MONGODB_URL)
        db = client[DB_NAME]
        
        total_users = db.Users.count_documents({})
        
        # Get user details for Redis online users
        online_users = []
        for user_id in redis_online_user_ids:
            user = db.Users.find_one({"_id": ObjectId(user_id)})
            if user:
                online_users.append({
                    "id": str(user["_id"]),
                    "name": user.get("name"),
                    "email": user.get("email"),
                    "role": user.get("role")
                })
        
        offline_count = total_users - redis_online_count
        
        client.close()
        
        return {
            "total_users": total_users,
            "online_users": redis_online_count,
            "offline_users": offline_count,
            "online_user_details": online_users
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))