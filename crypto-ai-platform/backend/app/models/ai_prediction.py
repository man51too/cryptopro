"""
AI Prediction models
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class AIPrediction(Base):
    """
    AI prediction results for coins
    """
    __tablename__ = "ai_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    coin_id = Column(String(100), ForeignKey('coins.coin_id'), nullable=False, index=True)
    
    # AI Scores
    ai_recovery_score = Column(Float, nullable=True)  # 0-100
    recovery_probability = Column(Float, nullable=True)  # 0-100 (percentage)
    
    # Time Estimates
    estimated_recovery_months_min = Column(Float, nullable=True)
    estimated_recovery_months_max = Column(Float, nullable=True)
    
    # Risk Assessment
    risk_level = Column(String(20), nullable=True)  # Low, Medium, High, Very High
    
    # Component Scores
    technical_score = Column(Float, nullable=True)  # 0-100
    fundamental_score = Column(Float, nullable=True)  # 0-100
    onchain_score = Column(Float, nullable=True)  # 0-100
    sentiment_score = Column(Float, nullable=True)  # 0-100
    historical_score = Column(Float, nullable=True)  # 0-100
    
    # Analysis Details
    analysis_reasons = Column(Text, nullable=True)  # JSON array of reasons as text
    bullish_signals = Column(Text, nullable=True)  # JSON array of bullish signals
    bearish_signals = Column(Text, nullable=True)  # JSON array of bearish signals
    
    # Model Metadata
    model_version = Column(String(50), nullable=True)
    confidence_level = Column(Float, nullable=True)  # Model confidence 0-100
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_ai_score', 'ai_recovery_score'),
        Index('idx_recovery_prob', 'recovery_probability'),
    )
    
    def __repr__(self):
        return f"<AIPrediction {self.coin_id} Score: {self.ai_recovery_score}>"


class AIRecoveryScore(Base):
    """
    Historical AI recovery scores for tracking changes over time
    """
    __tablename__ = "ai_recovery_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    coin_id = Column(String(100), nullable=False, index=True)
    
    # Score
    ai_score = Column(Float, nullable=False)
    recovery_probability = Column(Float, nullable=False)
    
    # Timestamp
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_coin_score_time', 'coin_id', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<AIRecoveryScore {self.coin_id} at {self.timestamp}>"
