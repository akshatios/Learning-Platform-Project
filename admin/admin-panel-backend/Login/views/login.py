import hashlib
from fastapi import HTTPException, status
from pydantic import BaseModel
from core.database import admin_collection
from helperFunction.jwt_helper import create_access_token

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: str

async def login(login_data: LoginRequest):
    # Find admin by email
    admin = await admin_collection.find_one({"email": login_data.email})
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    hashed_input = hashlib.sha256(login_data.password.encode()).hexdigest()
    if hashed_input != admin["password"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": str(admin["_id"])})
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=str(admin["_id"])
    )