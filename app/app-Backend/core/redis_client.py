import redis
from core.config import REDIS_URL

# Use sync Redis client
redis_client = None

def connect_redis_sync():
    global redis_client
    try:
        redis_client = redis.from_url(REDIS_URL, decode_responses=True)
        redis_client.ping()
        print("Connected to Redis (sync)")
        return True
    except Exception as e:
        print(f"Redis connection failed: {e}")
        redis_client = None
        return False

def close_redis_sync():
    global redis_client
    if redis_client:
        redis_client.close()
        print("Disconnected from Redis")

# User session functions (sync)
def set_user_online_sync(user_id: str):
    """Set user as online in Redis with 1 hour expiry"""
    global redis_client
    if not redis_client:
        connect_redis_sync()
    
    if redis_client:
        try:
            redis_client.setex(f"user:{user_id}:online", 3600, "true")
            print(f"User {user_id} set online in Redis")
        except Exception as e:
            print(f"Redis setex error: {e}")
    else:
        print("Redis client not available")

def set_user_offline_sync(user_id: str):
    """Remove user from online status"""
    global redis_client
    if not redis_client:
        connect_redis_sync()
    
    if redis_client:
        try:
            redis_client.delete(f"user:{user_id}:online")
            print(f"User {user_id} set offline in Redis")
        except Exception as e:
            print(f"Redis delete error: {e}")
    else:
        print("Redis client not available")

def get_online_users_count_sync() -> int:
    """Get total count of online users"""
    global redis_client
    if not redis_client:
        connect_redis_sync()
    
    if redis_client:
        try:
            keys = redis_client.keys("user:*:online")
            return len(keys)
        except Exception as e:
            print(f"Redis keys error: {e}")
    return 0

def get_all_online_users_sync() -> list:
    """Get list of all online user IDs"""
    global redis_client
    if not redis_client:
        connect_redis_sync()
    
    if redis_client:
        try:
            keys = redis_client.keys("user:*:online")
            user_ids = [key.split(":")[1] for key in keys]
            return user_ids
        except Exception as e:
            print(f"Redis keys error: {e}")
    return []