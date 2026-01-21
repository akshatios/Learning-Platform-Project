from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from pymongo import MongoClient
import random
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from core.config import EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASSWORD, MONGODB_URL, DB_NAME

router = APIRouter()

# MongoDB connection from .env
client = MongoClient(MONGODB_URL)
db = client[DB_NAME]
users_collection = db['Users']
otp_collection = db['OTP']

class VerifyEmail(BaseModel):
    email: EmailStr
    otp: str

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

@router.post('/verify-email')
def verify_email(data: VerifyEmail):
    try:
        otp_record = otp_collection.find_one({
            'email': data.email,
            'otp': data.otp,
            'verified': False,
            'expiry': {'$gt': datetime.now()}
        })
        
        if not otp_record:
            raise HTTPException(status_code=400, detail='Invalid or expired OTP')
        
        result = users_collection.update_one(
            {'email': data.email},
            {'$set': {'email_verified': True}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail='User not found')
        
        otp_collection.update_one(
            {'_id': otp_record['_id']},
            {'$set': {'verified': True}}
        )
        
        return {'message': 'Email verified successfully'}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))