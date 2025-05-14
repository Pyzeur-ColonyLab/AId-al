import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Telegram settings
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    
    # AWS settings
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    
    # Database settings
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    
    # Model settings
    MODEL_NAME = os.getenv("MODEL_NAME", "default_model")
    MODEL_PATH = os.getenv("MODEL_PATH", "./models/saved_models/")
    
    # API settings
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))

settings = Settings()