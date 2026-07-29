"""
Coin Database Models
Defines the schema for cryptocurrency data storage
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Index, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from ..db.base import Base


class Coin(Base):
    """
    Coin model representing a cryptocurrency.
    
    Stores basic information about each cryptocurrency including
    name, symbol, market cap rank, and ATH data.
    """
    
    __tablename__ = "coins"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Info
    coin_id = Column(String(100), unique=True, nullable=False, index=True)  # e.g., "bitcoin"
    symbol = Column(String(20), nullable=False, index=True)  # e.g., "BTC"
    name = Column(String(100), nullable=False)
    
    # Market Data
    market_cap_rank = Column(Integer, nullable=True, index=True)
    current_price = Column(Float, nullable=True)
    market_cap = Column(Float, nullable=True)
    total_volume = Column(Float, nullable=True)
    
    # ATH Data
    ath = Column(Float, nullable=True)
    ath_date = Column(DateTime, nullable=True)
    ath_change_percentage = Column(Float, nullable=True)  # Percentage change from ATH
    
    # Supply Data
    circulating_supply = Column(Float, nullable=True)
    total_supply = Column(Float, nullable=True)
    max_supply = Column(Float, nullable=True)
    
    # Additional Info
    description = Column(Text, nullable=True)
    website = Column(String(500), nullable=True)
    blockchain = Column(String(100), nullable=True)
    launch_date = Column(DateTime, nullable=True)
    
    # Holder Data (if available)
    holder_count = Column(Integer, nullable=True)
    
    # Metadata
    is_active = Column(Boolean, default=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=func.now())
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    price_history = relationship("CoinPriceData", back_populates="coin", cascade="all, delete-orphan")
    ai_predictions = relationship("AIPrediction", back_populates="coin", cascade="all, delete-orphan")
    watchlists = relationship("WatchlistItem", back_populates="coin", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_coin_symbol', 'symbol'),
        Index('idx_coin_market_cap_rank', 'market_cap_rank'),
        Index('idx_coin_ath_change', 'ath_change_percentage'),
        Index('idx_coin_is_active', 'is_active'),
    )
    
    def __repr__(self):
        return f"<Coin(id={self.id}, symbol={self.symbol}, name={self.name})>"
    
    @property
    def distance_from_ath(self) -> float | None:
        """Calculate percentage distance from ATH"""
        if self.ath and self.current_price:
            return ((self.current_price - self.ath) / self.ath) * 100
        return None
    
    @property
    def required_growth_to_ath(self) -> float | None:
        """Calculate multiplier needed to reach ATH"""
        if self.ath and self.current_price and self.current_price > 0:
            return self.ath / self.current_price
        return None


class CoinPriceData(Base):
    """
    Historical price data for coins.
    
    Stores time-series price data for technical analysis.
    Uses TimescaleDB hypertable in production for better performance.
    """
    
    __tablename__ = "coin_price_data"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Key
    coin_id = Column(Integer, ForeignKey("coins.id"), nullable=False, index=True)
    
    # Price Data
    timestamp = Column(DateTime, nullable=False, index=True)
    open_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    
    # Timeframe (1m, 5m, 15m, 1h, 4h, 1d, 1w)
    timeframe = Column(String(10), nullable=False, default="1d")
    
    # Technical Indicators (pre-calculated)
    rsi = Column(Float, nullable=True)
    macd = Column(Float, nullable=True)
    macd_signal = Column(Float, nullable=True)
    ema_20 = Column(Float, nullable=True)
    ema_50 = Column(Float, nullable=True)
    sma_200 = Column(Float, nullable=True)
    bollinger_upper = Column(Float, nullable=True)
    bollinger_lower = Column(Float, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    coin = relationship("Coin", back_populates="price_history")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_price_coin_timestamp', 'coin_id', 'timestamp'),
        Index('idx_price_timestamp', 'timestamp'),
        Index('idx_price_timeframe', 'timeframe'),
    )
    
    def __repr__(self):
        return f"<CoinPriceData(coin_id={self.coin_id}, timestamp={self.timestamp}, close={self.close_price})>"


# Import ForeignKey after Base is defined
from sqlalchemy import ForeignKey
