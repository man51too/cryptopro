"""
AI Prediction Pydantic Schemas
Defines data validation and serialization schemas for AI predictions
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class AIPredictionBase(BaseModel):
    """Base schema for AI prediction data"""
    ai_recovery_score: float = Field(ge=0, le=100)
    recovery_probability: float = Field(ge=0, le=100)
    
    class Config:
        from_attributes = True


class AIPredictionResponse(AIPredictionBase):
    """Complete AI prediction response schema"""
    id: int
    coin_id: int
    
    # Component Scores
    technical_score: Optional[float] = None
    fundamental_score: Optional[float] = None
    onchain_score: Optional[float] = None
    sentiment_score: Optional[float] = None
    historical_score: Optional[float] = None
    
    # Predictions
    estimated_recovery_months: Optional[int] = None
    predicted_ath_price: Optional[float] = None
    confidence_interval_lower: Optional[float] = None
    confidence_interval_upper: Optional[float] = None
    
    # Risk Assessment
    risk_level: Optional[str] = None
    volatility_score: Optional[float] = None
    liquidity_score: Optional[float] = None
    
    # Analysis Details
    analysis_reasons: Optional[List[str]] = None
    technical_indicators: Optional[Dict[str, Any]] = None
    fundamental_metrics: Optional[Dict[str, Any]] = None
    onchain_metrics: Optional[Dict[str, Any]] = None
    sentiment_metrics: Optional[Dict[str, Any]] = None
    
    # Model Metadata
    model_version: Optional[str] = None
    model_confidence: Optional[float] = None
    
    # Timestamps
    prediction_date: datetime
    valid_until: Optional[datetime] = None
    
    @property
    def recommendation(self) -> str:
        """Generate investment recommendation"""
        if self.ai_recovery_score >= 80 and self.recovery_probability >= 70:
            return "STRONG BUY"
        elif self.ai_recovery_score >= 65 and self.recovery_probability >= 55:
            return "BUY"
        elif self.ai_recovery_score >= 50 and self.recovery_probability >= 40:
            return "HOLD"
        elif self.ai_recovery_score >= 35:
            return "WEAK HOLD"
        else:
            return "SELL/AVOID"
    
    class Config:
        from_attributes = True


class MoonshotCandidateResponse(BaseModel):
    """Schema for moonshot candidate coins"""
    id: int
    coin_id: int
    symbol: str
    name: str
    
    # Price Data
    current_price: Optional[float] = None
    ath: Optional[float] = None
    distance_from_ath: Optional[float] = None
    required_growth_to_ath: Optional[float] = None
    
    # AI Scores
    ai_recovery_score: float
    recovery_probability: float
    
    # Predictions
    estimated_recovery_months: Optional[int] = None
    risk_level: Optional[str] = None
    recommendation: str
    
    # Reasons
    reasons: List[str] = []
    
    class Config:
        from_attributes = True


class AIScoreResponse(BaseModel):
    """Simplified AI score response"""
    id: int
    coin_id: int
    symbol: str
    name: str
    
    # Scores
    ai_recovery_score: float
    recovery_probability: float
    technical_score: Optional[float] = None
    fundamental_score: Optional[float] = None
    onchain_score: Optional[float] = None
    sentiment_score: Optional[float] = None
    historical_score: Optional[float] = None
    
    # Recommendation
    recommendation: str
    
    class Config:
        from_attributes = True


class BacktestResultResponse(BaseModel):
    """Schema for backtesting results"""
    id: int
    test_name: str
    start_date: datetime
    end_date: datetime
    initial_capital: float
    
    # Performance Metrics
    total_return: Optional[float] = None
    annualized_return: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    max_drawdown: Optional[float] = None
    win_rate: Optional[float] = None
    profit_factor: Optional[float] = None
    
    # Accuracy
    accuracy_1month: Optional[float] = None
    accuracy_3months: Optional[float] = None
    accuracy_6months: Optional[float] = None
    accuracy_1year: Optional[float] = None
    
    # Results
    total_predictions: Optional[int] = None
    successful_predictions: Optional[int] = None
    average_roi: Optional[float] = None
    
    class Config:
        from_attributes = True
