"""Pydantic schemas for AI prediction data."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime


class AIPredictionBase(BaseModel):
    """Base AI prediction schema."""
    
    coin_id: int


class AIPredictionCreate(AIPredictionBase):
    """Schema for creating an AI prediction."""
    
    ai_score: float = Field(..., ge=0, le=100)
    recovery_probability: float = Field(..., ge=0, le=1)
    estimated_months_to_ath: Optional[int] = Field(None, ge=1)
    risk_level: str = Field(..., pattern="^(Low|Medium|High|Very High)$")
    technical_score: float = Field(..., ge=0, le=100)
    fundamental_score: float = Field(..., ge=0, le=100)
    onchain_score: float = Field(..., ge=0, le=100)
    sentiment_score: float = Field(..., ge=0, le=100)
    historical_score: float = Field(..., ge=0, le=100)
    key_factors: List[str] = []
    confidence_interval: Optional[Dict[str, float]] = None


class AIPredictionUpdate(BaseModel):
    """Schema for updating an AI prediction."""
    
    ai_score: Optional[float] = Field(None, ge=0, le=100)
    recovery_probability: Optional[float] = Field(None, ge=0, le=1)
    estimated_months_to_ath: Optional[int] = Field(None, ge=1)
    risk_level: Optional[str] = Field(None, pattern="^(Low|Medium|High|Very High)$")
    key_factors: Optional[List[str]] = None


class AIPredictionInDB(AIPredictionBase):
    """Schema for AI prediction in database."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    ai_score: float
    recovery_probability: float
    estimated_months_to_ath: Optional[int]
    risk_level: str
    technical_score: float
    fundamental_score: float
    onchain_score: float
    sentiment_score: float
    historical_score: float
    key_factors: List[str]
    confidence_interval: Optional[Dict[str, Any]] = None
    model_version: str
    created_at: datetime
    updated_at: datetime


class AIPrediction(AIPredictionInDB):
    """Public AI prediction schema."""
    
    coin_symbol: Optional[str] = None
    coin_name: Optional[str] = None
    current_price: Optional[float] = None
    ath_price: Optional[float] = None


class AIRecoveryScore(BaseModel):
    """Schema for AI recovery score analysis."""
    
    coin_id: int
    symbol: str
    name: str
    ai_score: float
    recovery_probability: float
    estimated_months: Optional[int]
    risk_level: str
    rank: int


class MoonshotCandidate(BaseModel):
    """Schema for moonshot candidate."""
    
    coin_id: int
    symbol: str
    name: str
    current_price: float
    ath_price: float
    distance_from_ath: float
    ai_score: float
    recovery_probability: float
    estimated_months: Optional[int]
    risk_level: str
    key_reasons: List[str]
    technical_signals: List[str]
    fundamental_strengths: List[str]


class TechnicalIndicators(BaseModel):
    """Schema for technical indicators."""
    
    rsi: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    ema_20: Optional[float] = None
    ema_50: Optional[float] = None
    sma_200: Optional[float] = None
    bollinger_upper: Optional[float] = None
    bollinger_middle: Optional[float] = None
    bollinger_lower: Optional[float] = None
    atr: Optional[float] = None
    adx: Optional[float] = None
    stochastic_k: Optional[float] = None
    stochastic_d: Optional[float] = None
    vwap: Optional[float] = None
    supertrend: Optional[float] = None
    trend: Optional[str] = None


class BacktestResult(BaseModel):
    """Schema for backtest results."""
    
    total_predictions: int
    correct_predictions: int
    accuracy: float
    avg_return: float
    max_drawdown: float
    sharpe_ratio: Optional[float] = None
    period_start: datetime
    period_end: datetime
    by_timeframe: Optional[Dict[str, float]] = None
