"""SQLAlchemy models for watchlist and alert tables."""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Index, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from typing import TYPE_CHECKING, Optional, List
import enum

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.coin import Coin


class AlertTypeEnum(str, enum.Enum):
    """Alert type enumeration for database."""
    
    PRICE_ABOVE = "price_above"
    PRICE_BELOW = "price_below"
    SCORE_INCREASE = "score_increase"
    SCORE_DECREASE = "score_decrease"
    ATH_RECOVERY = "ath_recovery"


class NotificationMethodEnum(str, enum.Enum):
    """Notification method enumeration for database."""
    
    EMAIL = "email"
    WEBHOOK = "webhook"
    PUSH = "push"


class Watchlist(Base):
    """Watchlist model for user's favorite coins."""
    
    __tablename__ = "watchlists"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="watchlists")
    items: Mapped[List["WatchlistItem"]] = relationship(
        "WatchlistItem", back_populates="watchlist", cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Watchlist(id={self.id}, name={self.name}, user_id={self.user_id})>"


class WatchlistItem(Base):
    """Watchlist item model linking watchlists to coins."""
    
    __tablename__ = "watchlist_items"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    watchlist_id: Mapped[int] = mapped_column(Integer, ForeignKey("watchlists.id"), nullable=False, index=True)
    coin_id: Mapped[int] = mapped_column(Integer, ForeignKey("coins.id"), nullable=False, index=True)
    custom_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    added_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    watchlist: Mapped["Watchlist"] = relationship("Watchlist", back_populates="items")
    coin: Mapped["Coin"] = relationship("Coin", back_populates="watchlist_items")
    
    # Unique constraint
    __table_args__ = (
        Index("ix_watchlist_items_unique", "watchlist_id", "coin_id", unique=True),
    )
    
    def __repr__(self) -> str:
        return f"<WatchlistItem(watchlist_id={self.watchlist_id}, coin_id={self.coin_id})>"


class Alert(Base):
    """Alert model for user notifications."""
    
    __tablename__ = "alerts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    alert_type: Mapped[AlertTypeEnum] = mapped_column(SQLEnum(AlertTypeEnum), nullable=False)
    coin_id: Mapped[int] = mapped_column(Integer, ForeignKey("coins.id"), nullable=False, index=True)
    threshold_value: Mapped[float] = mapped_column(Float, nullable=False)
    notification_methods: Mapped[List[str]] = mapped_column(
        String(255), 
        default="email"  # Comma-separated list
    )
    webhook_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    message_template: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    triggered_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="alerts")
    coin: Mapped["Coin"] = relationship("Coin")
    
    def __repr__(self) -> str:
        return f"<Alert(id={self.id}, type={self.alert_type}, coin_id={self.coin_id})>"


class AlertHistory(Base):
    """Alert history for tracking triggered alerts."""
    
    __tablename__ = "alert_history"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    alert_id: Mapped[int] = mapped_column(Integer, ForeignKey("alerts.id"), nullable=False, index=True)
    triggered_value: Mapped[float] = mapped_column(Float, nullable=False)
    notification_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    triggered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self) -> str:
        return f"<AlertHistory(alert_id={self.alert_id}, triggered_at={self.triggered_at})>"
