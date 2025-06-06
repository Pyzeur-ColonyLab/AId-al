import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Universal settings for the AI Bot
    Supports any HuggingFace model with flexible configuration
    """
    
    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN: str
    WEBHOOK_URL: Optional[str] = None
    WEBHOOK_PORT: int = 8000
    
    # Model Configuration - Easy to change for any HuggingFace model
    MODEL_NAME: str = "microsoft/DialoGPT-medium"  # Default model
    MODEL_TYPE: str = "universal"  # universal, transformer, auto
    MODEL_PATH: Optional[str] = None  # Local path if needed
    
    # Model Performance Settings
    MAX_LENGTH: int = 512
    BATCH_SIZE: int = 1
    USE_QUANTIZATION: bool = False  # Enable for large models on limited GPU
    DEVICE: str = "auto"  # auto, cpu, cuda
    
    # Generation Parameters
    TEMPERATURE: float = 0.7
    TOP_P: float = 0.9
    TOP_K: int = 50
    REPETITION_PENALTY: float = 1.1
    DO_SAMPLE: bool = True
    
    # HuggingFace Configuration
    HF_TOKEN: Optional[str] = None  # HuggingFace token for private models
    TRANSFORMERS_CACHE: str = "/tmp/transformers_cache"
    HF_HOME: str = "/tmp/huggingface"
    
    # Database Configuration
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "aibot_db"
    DB_USER: str = "botuser"
    DB_PASSWORD: str = "botpass"
    DATABASE_URL: Optional[str] = None
    
    # Redis Configuration (optional)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    # AWS Configuration (optional)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_DEFAULT_REGION: str = "us-east-1"
    
    # Application Configuration
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    MAX_WORKERS: int = 2
    
    # Bot Behavior
    DEFAULT_CONFIDENCE_THRESHOLD: float = 0.5
    MAX_RESPONSE_LENGTH: int = 1000
    ENABLE_LOGGING: bool = True
    RATE_LIMIT_PER_MINUTE: int = 10
    
    # Security
    ALLOWED_USERS: Optional[str] = None  # Comma-separated user IDs
    ADMIN_USERS: Optional[str] = None  # Comma-separated admin user IDs
    
    # Feature Flags
    ENABLE_URL_RESOURCES: bool = True
    ENABLE_SMART_CONTRACTS: bool = True
    ENABLE_MODEL_INFO_COMMAND: bool = True
    ENABLE_METRICS: bool = False
    
    # Monitoring
    METRICS_PORT: int = 9090
    HEALTH_CHECK_PORT: int = 8001
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Auto-generate DATABASE_URL if not provided
        if not self.DATABASE_URL:
            self.DATABASE_URL = f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        
        # Create cache directories
        os.makedirs(self.TRANSFORMERS_CACHE, exist_ok=True)
        os.makedirs(self.HF_HOME, exist_ok=True)
        
        # Set environment variables for HuggingFace
        os.environ["TRANSFORMERS_CACHE"] = self.TRANSFORMERS_CACHE
        os.environ["HF_HOME"] = self.HF_HOME
        
        if self.HF_TOKEN:
            os.environ["HF_TOKEN"] = self.HF_TOKEN
    
    @property
    def allowed_user_ids(self) -> list:
        """Get list of allowed user IDs"""
        if not self.ALLOWED_USERS:
            return []
        return [int(uid.strip()) for uid in self.ALLOWED_USERS.split(",") if uid.strip()]
    
    @property
    def admin_user_ids(self) -> list:
        """Get list of admin user IDs"""
        if not self.ADMIN_USERS:
            return []
        return [int(uid.strip()) for uid in self.ADMIN_USERS.split(",") if uid.strip()]
    
    def is_user_allowed(self, user_id: int) -> bool:
        """Check if user is allowed to use the bot"""
        if not self.allowed_user_ids:  # If no restrictions, allow all
            return True
        return user_id in self.allowed_user_ids
    
    def is_admin_user(self, user_id: int) -> bool:
        """Check if user is an admin"""
        return user_id in self.admin_user_ids
    
    def get_model_config(self) -> dict:
        """Get model configuration dictionary"""
        return {
            "model_name": self.MODEL_NAME,
            "model_type": self.MODEL_TYPE,
            "max_length": self.MAX_LENGTH,
            "temperature": self.TEMPERATURE,
            "top_p": self.TOP_P,
            "top_k": self.TOP_K,
            "repetition_penalty": self.REPETITION_PENALTY,
            "do_sample": self.DO_SAMPLE,
            "use_quantization": self.USE_QUANTIZATION,
            "device": self.DEVICE,
            "batch_size": self.BATCH_SIZE
        }

# Create global settings instance
settings = Settings()
