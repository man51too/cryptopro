"""
AI Prediction Database Models
Defines the schema for AI predictions and recovery scores
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Index, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from ..db.base import Base


class AIPrediction(Base):
    """
    AI Prediction model storing comprehensive analysis results.
    
    Contains all AI-generated predictions including recovery probability,
    risk assessment, and detailed analysis breakdown.
    """
    
    __tablename__ = "ai_predictions"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Key
    coin_id = Column(Integer, ForeignKey("coins.id"), nullable=False, index=True)
    
    # Overall Scores
    ai_recovery_score = Column(Float, nullable=False)  # 0-100
    recovery_probability = Column(Float, nullable=False)  # 0-100 (%)
    
    # Component Scores (weighted)
    technical_score = Column(Float, nullable=True)  # 30%
    fundamental_score = Column(Float, nullable=True)  # 25%
    onchain_score = Column(Float, nullable=True)  # 20%
    sentiment_score = Column(Float, nullable=True)  # 15%
    historical_score = Column(Float, nullable=True)  # 10%
    
    # Predictions
    estimated_recovery_months = Column(Integer, nullable=True)  # Estimated months to ATH
    predicted_ath_price = Column(Float, nullable=True)
    confidence_interval_lower = Column(Float, nullable=True)
    confidence_interval_upper = Column(Float, nullable=True)
    
    # Risk Assessment
    risk_level = Column(String(20), nullable=True)  # Low, Medium, High, Very High
    volatility_score = Column(Float, nullable=True)
    liquidity_score = Column(Float, nullable=True)
    
    # Analysis Details
    analysis_reasons = Column(JSON, nullable=True)  # Array of reason strings
    technical_indicators = Column(JSON, nullable=True)  # RSI, MACD, etc.
    fundamental_metrics = Column(JSON, nullable=True)  # Market cap rank, TVL, etc.
    onchain_metrics = Column(JSON, nullable=True)  # Whale activity, holder growth
    sentiment_metrics = Column(JSON, nullable=True)  # Social sentiment data
    
    # Model Metadata
    model_version = Column(String(50), nullable=True)
    model_confidence = Column(Float, nullable=True)
    features_used = Column(JSON, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)  # Manually verified by analysts
    
    # Timestamps
    prediction_date = Column(DateTime, default=func.now(), index=True)
    valid_until = Column(DateTime, nullable=True)
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now())
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    coin = relationship("Coin", back_populates="ai_predictions")
    
    # Indexes
    __table_args__ = (
        Index('idx_ai_coin_prediction', 'coin_id', 'prediction_date'),
        Index('idx_ai_recovery_score', 'ai_recovery_score'),
        Index('idx_ai_recovery_prob', 'recovery_probability'),
        Index('idx_ai_risk_level', 'risk_level'),
        Index('idx_ai_is_active', 'is_active'),
    )
    
    def __repr__(self):
        return f"<AIPrediction(coin_id={self.coin_id}, score={self.ai_recovery_score}, prob={self.recovery_probability}%)>"
    
    @property
    def recommendation(self) -> str:
        """Generate investment recommendation based on scores"""
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
    
    @property
    def score_breakdown(self) -> dict:
        """Return weighted score breakdown"""
        return {
            "technical": {"score": self.technical_score, "weight": 0.30},
            "fundamental": {"score": self.fundamental_score, "weight": 0.25},
            "onchain": {"score": self.onchain_score, "weight": 0.20},
            "sentiment": {"score": self.sentiment_score, "weight": 0.15},
            "historical": {"score": self.historical_score, "weight": 0.10},
        }


class AIRecoveryScore(Base):
    """
    Historical AI Recovery Score tracking.
    
    Stores time-series data of AI scores for backtesting and trend analysis.
    """
    
    __tablename__ = "ai_recovery_scores"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Key
    coin_id = Column(Integer, ForeignKey("coins.id"), nullable=False, index=True)
    
    # Score Data
    ai_score = Column(Float, nullable=False)
    recovery_probability = Column(Float, nullable=False)
    
    # Price Context
    price_at_prediction = Column(Float, nullable=False)
    ath_at_prediction = Column(Float, nullable=False)
    distance_from_ath = Column(Float, nullable=False)
    
    # Outcome Tracking (for backtesting)
    actual_recovery_achieved = Column(Boolean, nullable=True)
    days_to_recovery = Column(Integer, nullable=True)
    max_price_after_prediction = Column(Float, nullable=True)
    roi_after_prediction = Column(Float, nullable=True)
    
    # Timeframe
    prediction_horizon_days = Column(Integer, nullable=True)  # e.g., 30, 90, 180
    
    # Metadata
    scored_at = Column(DateTime, default=func.now(), index=True)
    created_at = Column(DateTime, default=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_ai_score_coin_time', 'coin_id', 'scored_at'),
        Index('idx_ai_score_value', 'ai_score'),
        Index('idx_ai_score_achieved', 'actual_recovery_achieved'),
    )
    
    def __repr__(self):
        return f"<AIRecoveryScore(coin_id={self.coin_id}, score={self.ai_score}, achieved={self.actual_recovery_achieved})>"


class BacktestResult(Base):
    """
    Backtesting results for AI model validation.
    
    Stores historical performance metrics of AI predictions.
    """
    
    __tablename__ = "backtest_results"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Test Configuration
    test_name = Column(String(100), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    initial_capital = Column(Float, nullable=False)
    
    # Performance Metrics
    total_return = Column(Float, nullable=True)  # Percentage
    annualized_return = Column(Float, nullable=True)
    sharpe_ratio = Column(Float, nullable=True)
    max_drawdown = Column(Float, nullable=True)
    win_rate = Column(Float, nullable=True)  # Percentage of profitable trades
    profit_factor = Column(Float, nullable=True)
    
    # Prediction Accuracy
    accuracy_1month = Column(Float, nullable=True)
    accuracy_3months = Column(Float, nullable=True)
    accuracy_6months = Column(Float, nullable=True)
    accuracy_1year = Column(Float, nullable=True)
    
    # Detailed Results
    total_predictions = Column(Integer, nullable=True)
    successful_predictions = Column(Integer, nullable=True)
    average_roi = Column(Float, nullable=True)
    best_trade = Column(Float, nullable=True)
    worst_trade = Column(Float, nullable=True)
    
    # Model Info
    model_version = Column(String(50), nullable=True)
    parameters_used = Column(JSON, nullable=True)
    
    # Status
    is_completed = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_backtest_name', 'test_name'),
        Index('idx_backtest_dates', 'start_date', 'end_date'),
        Index('idx_backtest_completed', 'is_completed'),
    )
    
    def __repr__(self):
        return f"<BacktestResult(name={self.test_name}, return={self.total_return}%, win_rate={self.win_rate}%)>"
