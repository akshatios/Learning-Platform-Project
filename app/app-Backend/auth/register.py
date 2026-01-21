from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from typing import Literal
import random
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from core.config import EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASSWORD, MONGODB_URL, DB_NAME

# MongoDB connection
client = MongoClient(MONGODB_URL)
db = client[DB_NAME]
users_collection = db['Users']
otp_collection = db['OTP']

router = APIRouter()

class RegisterUser(BaseModel):
    name: str
    email: EmailStr
    role: Literal['student', 'Teacher']
    password: str
    confirm_password: str

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(email, otp):
    try:
        msg = MIMEText(f"Your OTP for email verification is: {otp}")
        msg['Subject'] = 'Email Verification OTP'
        msg['From'] = EMAIL_USER
        msg['To'] = email
        
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

@router.post('/register')
def register_user(user: RegisterUser):
    try:
        if user.password != user.confirm_password:
            raise HTTPException(status_code=400, detail='Passwords do not match')
        
        if users_collection.find_one({'email': user.email}):
            raise HTTPException(status_code=400, detail='User already exists')
        
        hashed_password = generate_password_hash(user.password)
        
        # Generate OTP
        otp = generate_otp()
        otp_expiry = datetime.now() + timedelta(minutes=10)
        
        # Store user data (unverified)
        user_data = {
            'name': user.name,
            'email': user.email,
            'role': user.role,
            'password': hashed_password,
            'email_verified': False
        }
        result = users_collection.insert_one(user_data)
        
        # Store OTP
        otp_collection.delete_many({'email': user.email})  # Delete old OTPs
        otp_data = {
            'email': user.email,
            'otp': otp,
            'expiry': otp_expiry,
            'verified': False
        }
        otp_collection.insert_one(otp_data)
        
        # Send OTP email
        if send_otp_email(user.email, otp):
            return {
                'message': 'User registered successfully. OTP sent to your email.',
                'user_id': str(result.inserted_id)
            }
        else:
            return {
                'message': 'User registered but failed to send OTP. Please request OTP manually.',
                'user_id': str(result.inserted_id)
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))