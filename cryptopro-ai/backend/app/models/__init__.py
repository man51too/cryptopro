"""Models module initialization."""

from app.models.user import User
from app.models.coin import Coin, CoinPriceHistory
from app.models.ai_prediction import AIPrediction, BacktestResult
from app.models.watchlist import (
    Watchlist,
    WatchlistItem,
    Alert,
    AlertHistory,
    AlertTypeEnum,
    NotificationMethodEnum,
)

__all__ = [
    "User",
    "Coin",
    "CoinPriceHistory",
    "AIPrediction",
    "BacktestResult",
    "Watchlist",
    "WatchlistItem",
    "Alert",
    "AlertHistory",
    "AlertTypeEnum",
    "NotificationMethodEnum",
]
