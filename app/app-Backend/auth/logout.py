from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId
from core.config import MONGODB_URL, DB_NAME

router = APIRouter()

class LogoutUser(BaseModel):
    user_id: str

@router.post('/logout')
def logout_user(user: LogoutUser):
    try:
        # Set user offline in Redis
        from core.redis_client import set_user_offline_sync
        set_user_offline_sync(user.user_id)
        
        # Update isActive to False in database using sync client
        client = MongoClient(MONGODB_URL)
        db = client[DB_NAME]
        
        result = db.Users.update_one(
            {"_id": ObjectId(user.user_id)},
            {"$set": {"isActive": False}}
        )
        print(f"User {user.user_id} set inactive in database")
        
        client.close()
        
        return {
            'message': 'Logout successful',
            'user_id': user.user_id,
            'isActive': False
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))