import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    MONGODB_URL: str = os.getenv("MONGODB_URL")
    DB_NAME: str = os.getenv("DB_NAME")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALLOWED_HOSTS: list = ["localhost", "127.0.0.1", "0.0.0.0"]

settings = Settings()