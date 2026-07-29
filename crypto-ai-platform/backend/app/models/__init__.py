"""
Database models for the Crypto AI Platform
"""
from app.models.coin import Coin, CoinData
from app.models.ai_prediction import AIPrediction, AIRecoveryScore
from app.models.user import User
from app.models.watchlist import Watchlist

__all__ = [
    "Coin",
    "CoinData",
    "AIPrediction",
    "AIRecoveryScore",
    "User",
    "Watchlist",
]
