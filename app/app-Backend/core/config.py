import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # MongoDB Configuration
    MONGODB_URL: str = os.getenv("MONGODB_URL")
    DB_NAME: str = os.getenv("DB_NAME")
    
    # JWT Configuration
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET", "your-secret-key-here")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Email Configuration
    EMAIL_HOST: str = "smtp.gmail.com"
    EMAIL_PORT: int = 587
    EMAIL_USER: str = os.getenv("EMAIL_USER")
    EMAIL_PASSWORD: str = os.getenv("EMAIL_PASSWORD")
    
    # Redis Configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Cloudinary Configuration
    CLOUDINARY_CLOUD_NAME: str = os.getenv("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY: str = os.getenv("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET: str = os.getenv("CLOUDINARY_API_SECRET")
    
    # Stripe Configuration
    STRIPE_PUBLISHABLE_KEY: str = os.getenv("STRIPE_PUBLISHABLE_KEY")
    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY")

settings = Settings()

# Backward compatibility - keeping old variable names
MONGODB_URL = settings.MONGODB_URL
DB_NAME = settings.DB_NAME
JWT_SECRET = settings.JWT_SECRET_KEY
EMAIL_HOST = settings.EMAIL_HOST
EMAIL_PORT = settings.EMAIL_PORT
EMAIL_USER = settings.EMAIL_USER
EMAIL_PASSWORD = settings.EMAIL_PASSWORD
REDIS_URL = settings.REDIS_URL
CLOUDINARY_CLOUD_NAME = settings.CLOUDINARY_CLOUD_NAME
CLOUDINARY_API_KEY = settings.CLOUDINARY_API_KEY
CLOUDINARY_API_SECRET = settings.CLOUDINARY_API_SECRET
STRIPE_PUBLISHABLE_KEY = settings.STRIPE_PUBLISHABLE_KEY
STRIPE_SECRET_KEY = settings.STRIPE_SECRET_KEY