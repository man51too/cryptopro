"""
Core configuration for the Crypto AI Platform
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "Crypto AI Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/crypto_ai"
    DATABASE_ASYNC_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/crypto_ai"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    
    # API Keys
    COINGECKO_API_KEY: Optional[str] = None
    COINMARKETCAP_API_KEY: Optional[str] = None
    BINANCE_API_KEY: Optional[str] = None
    BINANCE_API_SECRET: Optional[str] = None
    GLASSNODE_API_KEY: Optional[str] = None
    SANTIMENT_API_KEY: Optional[str] = None
    LUNARCRUSH_API_KEY: Optional[str] = None
    
    # JWT
    JWT_SECRET_KEY: str = "your-super-secret-jwt-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # AI Model Settings
    MODEL_PATH: str = "./models"
    ENABLE_TECHNICAL_ANALYSIS: bool = True
    ENABLE_FUNDAMENTAL_ANALYSIS: bool = True
    ENABLE_ONCHAIN_ANALYSIS: bool = True
    ENABLE_SENTIMENT_ANALYSIS: bool = True
    
    # Scoring Weights
    TECHNICAL_WEIGHT: float = 0.30
    FUNDAMENTAL_WEIGHT: float = 0.25
    ONCHAIN_WEIGHT: float = 0.20
    SENTIMENT_WEIGHT: float = 0.15
    HISTORICAL_WEIGHT: float = 0.10
    
    # Data Refresh Intervals (seconds)
    PRICE_REFRESH_INTERVAL: int = 30
    AI_SCORE_REFRESH_INTERVAL: int = 300
    ATH_SCAN_INTERVAL: int = 60
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance"""
    return settings
