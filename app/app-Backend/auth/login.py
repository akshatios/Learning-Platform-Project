from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from pymongo import MongoClient
from werkzeug.security import check_password_hash
from bson import ObjectId
from core.config import MONGODB_URL, DB_NAME
from helperFunction.jwt_helper import create_access_token

# MongoDB connection
client = MongoClient(MONGODB_URL)
db = client[DB_NAME]
users_collection = db['Users']

router = APIRouter()

class LoginUser(BaseModel):
    email: EmailStr
    password: str

@router.post('/login')
def login_user(user: LoginUser):
    try:
        # Use sync client for finding user
        user_data = users_collection.find_one({'email': user.email})
        
        if not user_data:
            raise HTTPException(status_code=404, detail='User not found')
        
        if not user_data.get('email_verified', False):
            raise HTTPException(status_code=403, detail='Please verify your email first')
        
        if not check_password_hash(user_data['password'], user.password):
            raise HTTPException(status_code=401, detail='Invalid password')
        
        user_id = str(user_data['_id'])
        
        # Generate JWT token
        token_data = {
            "user_id": user_id,
            "email": user_data['email'],
            "role": user_data['role']
        }
        access_token = create_access_token(token_data)
        
        # Set user online in Redis
        from core.redis_client import set_user_online_sync
        set_user_online_sync(user_id)
        
        # Update isActive in database using sync client
        users_collection.update_one(
            {"_id": user_data['_id']},
            {"$set": {"isActive": True}}
        )
        print(f"User {user_id} set active in database")
        
        return {
            'message': 'Login successful',
            'access_token': access_token,
            'token_type': 'bearer',
            'user': {
                'id': user_id,
                'name': user_data['name'],
                'email': user_data['email'],
                'role': user_data['role'],
                'isActive': True
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))