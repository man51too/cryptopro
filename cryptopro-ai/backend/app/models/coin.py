"""SQLAlchemy models for coin-related tables."""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Index, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.ai_prediction import AIPrediction
    from app.models.watchlist import WatchlistItem


class Coin(Base):
    """Coin model for cryptocurrency data."""
    
    __tablename__ = "coins"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    symbol: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    coingecko_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True, index=True)
    coinmarketcap_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    rank: Mapped[int] = mapped_column(Integer, default=0, index=True)
    market_cap_usd: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    volume_24h_usd: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    circulating_supply: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    total_supply: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_supply: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ath_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ath_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    atl_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    atl_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    price_change_24h: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    price_change_percentage_24h: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    current_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    price_history: Mapped[List["CoinPriceHistory"]] = relationship(
        "CoinPriceHistory", back_populates="coin", cascade="all, delete-orphan"
    )
    predictions: Mapped[List["AIPrediction"]] = relationship(
        "AIPrediction", back_populates="coin", cascade="all, delete-orphan"
    )
    watchlist_items: Mapped[List["WatchlistItem"]] = relationship(
        "WatchlistItem", back_populates="coin", cascade="all, delete-orphan"
    )
    
    # Indexes
    __table_args__ = (
        Index("ix_coins_rank_is_active", "rank", "is_active"),
        Index("ix_coins_symbol_is_active", "symbol", "is_active"),
    )
    
    def __repr__(self) -> str:
        return f"<Coin(id={self.id}, symbol={self.symbol}, name={self.name})>"
    
    @property
    def ath_distance_percent(self) -> Optional[float]:
        """Calculate percentage distance from ATH."""
        if self.ath_price and self.current_price and self.ath_price > 0:
            return ((self.current_price - self.ath_price) / self.ath_price) * 100
        return None
    
    @property
    def required_growth_multiple(self) -> Optional[float]:
        """Calculate growth multiple needed to reach ATH."""
        if self.ath_price and self.current_price and self.current_price > 0:
            return self.ath_price / self.current_price
        return None


class CoinPriceHistory(Base):
    """Historical price data for coins (TimescaleDB hypertable compatible)."""
    
    __tablename__ = "coin_price_history"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    coin_id: Mapped[int] = mapped_column(Integer, ForeignKey("coins.id"), nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    price_usd: Mapped[float] = mapped_column(Float, nullable=False)
    market_cap_usd: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    volume_24h_usd: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    price_change_24h: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Relationship
    coin: Mapped["Coin"] = relationship("Coin", back_populates="price_history")
    
    # Indexes
    __table_args__ = (
        Index("ix_price_history_coin_timestamp", "coin_id", "timestamp"),
    )
    
    def __repr__(self) -> str:
        return f"<CoinPriceHistory(coin_id={self.coin_id}, timestamp={self.timestamp}, price={self.price_usd})>"
