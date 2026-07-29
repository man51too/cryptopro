"""Schemas module initialization."""

from app.schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserInDB,
    User,
    Token,
    TokenPayload,
    LoginRequest,
)

from app.schemas.coin import (
    CoinBase,
    CoinCreate,
    CoinUpdate,
    CoinInDB,
    Coin,
    CoinPriceData,
    CoinWithPrediction,
    ATHDistanceResponse,
    CoinListResponse,
)

from app.schemas.ai_prediction import (
    AIPredictionBase,
    AIPredictionCreate,
    AIPredictionUpdate,
    AIPredictionInDB,
    AIPrediction,
    AIRecoveryScore,
    MoonshotCandidate,
    TechnicalIndicators,
    BacktestResult,
)

from app.schemas.watchlist import (
    AlertType,
    NotificationMethod,
    WatchlistBase,
    WatchlistCreate,
    WatchlistUpdate,
    WatchlistInDB,
    Watchlist,
    WatchlistItem,
    AlertBase,
    AlertCreate,
    AlertUpdate,
    AlertInDB,
    Alert,
    AlertTrigger,
)

__all__ = [
    # User schemas
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserInDB",
    "User",
    "Token",
    "TokenPayload",
    "LoginRequest",
    # Coin schemas
    "CoinBase",
    "CoinCreate",
    "CoinUpdate",
    "CoinInDB",
    "Coin",
    "CoinPriceData",
    "CoinWithPrediction",
    "ATHDistanceResponse",
    "CoinListResponse",
    # AI Prediction schemas
    "AIPredictionBase",
    "AIPredictionCreate",
    "AIPredictionUpdate",
    "AIPredictionInDB",
    "AIPrediction",
    "AIRecoveryScore",
    "MoonshotCandidate",
    "TechnicalIndicators",
    "BacktestResult",
    # Watchlist & Alert schemas
    "AlertType",
    "NotificationMethod",
    "WatchlistBase",
    "WatchlistCreate",
    "WatchlistUpdate",
    "WatchlistInDB",
    "Watchlist",
    "WatchlistItem",
    "AlertBase",
    "AlertCreate",
    "AlertUpdate",
    "AlertInDB",
    "Alert",
    "AlertTrigger",
]
