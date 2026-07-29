"""
Core configuration for CryptoPro AI application.
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "CryptoPro AI"
    DEBUG: bool = False
    SECRET_KEY: str = "change-me-in-production-min-32-characters-secret-key"
    API_PREFIX: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/cryptopro"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # JWT Authentication
    JWT_SECRET_KEY: str = "change-me-jwt-secret-min-32-characters"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # External APIs
    COINGECKO_API_KEY: Optional[str] = None
    COINMARKETCAP_API_KEY: Optional[str] = None
    BINANCE_API_KEY: Optional[str] = None
    BINANCE_API_SECRET: Optional[str] = None
    GLASSNODE_API_KEY: Optional[str] = None
    SANTIMENT_API_KEY: Optional[str] = None
    ALTERNATIVE_ME_API_KEY: Optional[str] = None
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000"
    
    # WebSocket
    WS_UPDATE_INTERVAL: int = 5  # seconds
    
    # Data Sources
    DEFAULT_DATA_SOURCE: str = "coingecko"
    ENABLE_BINANCE_STREAM: bool = True
    
    # AI Configuration
    AI_MODEL_VERSION: str = "v1.0"
    MIN_CONFIDENCE_THRESHOLD: float = 0.6
    ENABLE_BACKTESTING: bool = True
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
