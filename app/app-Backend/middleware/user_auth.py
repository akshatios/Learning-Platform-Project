from fastapi import Depends, HTTPException, status, Request
from helperFunction.jwt_helper import get_user_from_token

async def get_current_user(request: Request):
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )
    
    token = auth_header.split(" ")[1]
    user_id = get_user_from_token(token)
    return user_id

async def check_user_authentication(current_user: str = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authenticated"
        )
    return current_user
