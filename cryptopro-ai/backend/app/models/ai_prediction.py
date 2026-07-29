"""SQLAlchemy models for AI prediction tables."""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Index, JSON, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from typing import TYPE_CHECKING, Optional, Dict, Any, List

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.coin import Coin


class AIPrediction(Base):
    """AI prediction model for cryptocurrency recovery analysis."""
    
    __tablename__ = "ai_predictions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    coin_id: Mapped[int] = mapped_column(Integer, ForeignKey("coins.id"), nullable=False, index=True)
    ai_score: Mapped[float] = mapped_column(Float, nullable=False)
    recovery_probability: Mapped[float] = mapped_column(Float, nullable=False)
    estimated_months_to_ath: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False)
    technical_score: Mapped[float] = mapped_column(Float, nullable=False)
    fundamental_score: Mapped[float] = mapped_column(Float, nullable=False)
    onchain_score: Mapped[float] = mapped_column(Float, nullable=False)
    sentiment_score: Mapped[float] = mapped_column(Float, nullable=False)
    historical_score: Mapped[float] = mapped_column(Float, nullable=False)
    key_factors: Mapped[List[str]] = mapped_column(JSON, default=list)
    confidence_interval: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    model_version: Mapped[str] = mapped_column(String(50), default="v1.0")
    is_latest: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    coin: Mapped["Coin"] = relationship("Coin", back_populates="predictions")
    
    # Indexes
    __table_args__ = (
        Index("ix_predictions_coin_is_latest", "coin_id", "is_latest"),
        Index("ix_predictions_ai_score", "ai_score", postgresql_using="btree"),
        Index("ix_predictions_created_at", "created_at", postgresql_using="btree"),
    )
    
    def __repr__(self) -> str:
        return f"<AIPrediction(id={self.id}, coin_id={self.coin_id}, ai_score={self.ai_score})>"


class BacktestResult(Base):
    """Backtest results for AI model validation."""
    
    __tablename__ = "backtest_results"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    total_predictions: Mapped[int] = mapped_column(Integer, nullable=False)
    correct_predictions: Mapped[int] = mapped_column(Integer, nullable=False)
    accuracy: Mapped[float] = mapped_column(Float, nullable=False)
    avg_return: Mapped[float] = mapped_column(Float, nullable=False)
    max_drawdown: Mapped[float] = mapped_column(Float, nullable=False)
    sharpe_ratio: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    period_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    metrics: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<BacktestResult(model={self.model_version}, accuracy={self.accuracy})>"
