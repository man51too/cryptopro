"""
Core Configuration Module
Handles all environment variables and application settings
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Core
    FASTAPI_ENV: str = "production"
    PROJECT_NAME: str = "CryptoPro AI"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://cryptopro:secure_password_123@postgres:5432/cryptopro_db"
    POSTGRES_USER: str = "cryptopro"
    POSTGRES_PASSWORD: str = "secure_password_123"
    POSTGRES_DB: str = "cryptopro_db"
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    
    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    
    # Security
    SECRET_KEY: str = "your-super-secret-key-change-in-production-min-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    FRONTEND_URL: str = "http://localhost:3000"
    ALLOWED_ORIGINS: str = "http://localhost:3000,https://cryptopro.ai"
    
    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    # API Keys
    COINGECKO_API_KEY: Optional[str] = None
    COINMARKETCAP_API_KEY: Optional[str] = None
    BINANCE_API_KEY: Optional[str] = None
    BINANCE_API_SECRET: Optional[str] = None
    GLASSNODE_API_KEY: Optional[str] = None
    SANTIMENT_API_KEY: Optional[str] = None
    LUNARCRUSH_API_KEY: Optional[str] = None
    
    # External APIs
    COINGECKO_BASE_URL: str = "https://pro-api.coingecko.com/api/v3"
    COINMARKETCAP_BASE_URL: str = "https://pro-api.coinmarketcap.com/v1"
    BINANCE_WS_URL: str = "wss://stream.binance.com:9443/ws"
    
    # AI/ML Settings
    AI_MODEL_PATH: str = "/app/models"
    ENABLE_LSTM: bool = True
    ENABLE_XGBOOST: bool = True
    ENABLE_TRANSFORMER: bool = True
    MOUNT_CARLO_SIMULATIONS: int = 1000
    
    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = 30
    WS_MAX_CONNECTIONS: int = 1000
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Monitoring
    PROMETHEUS_ENABLED: bool = True
    GRAFANA_ENABLED: bool = True
    
    # Celery
    CELERY_BROKER_URL: str = "redis://redis:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/2"
    
    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: str = "noreply@cryptopro.ai"
    
    # Feature Flags
    ENABLE_TECHNICAL_ANALYSIS: bool = True
    ENABLE_FUNDAMENTAL_ANALYSIS: bool = True
    ENABLE_ONCHAIN_ANALYSIS: bool = True
    ENABLE_SENTIMENT_ANALYSIS: bool = True
    ENABLE_BACKTESTING: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()
