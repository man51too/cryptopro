"""
Coin database models
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Index
from sqlalchemy.sql import func
from app.core.database import Base


class Coin(Base):
    """
    Coin model storing basic information about cryptocurrencies
    """
    __tablename__ = "coins"
    
    id = Column(Integer, primary_key=True, index=True)
    coin_id = Column(String(100), unique=True, nullable=False, index=True)  # CoinGecko ID
    symbol = Column(String(20), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    rank = Column(Integer, nullable=True, index=True)  # Market cap rank
    
    # Price Information
    current_price = Column(Float, nullable=True)
    ath = Column(Float, nullable=True)  # All-Time High
    ath_date = Column(DateTime, nullable=True)
    atl = Column(Float, nullable=True)  # All-Time Low
    atl_date = Column(DateTime, nullable=True)
    
    # Market Data
    market_cap = Column(Float, nullable=True)
    market_cap_rank = Column(Integer, nullable=True)
    volume_24h = Column(Float, nullable=True)
    circulating_supply = Column(Float, nullable=True)
    total_supply = Column(Float, nullable=True)
    max_supply = Column(Float, nullable=True)
    
    # ATH Analysis
    ath_distance_percent = Column(Float, nullable=True)  # e.g., -58.5 means 58.5% below ATH
    required_growth_multiplier = Column(Float, nullable=True)  # e.g., 2.42x needed to reach ATH
    
    # Blockchain Info
    blockchain = Column(String(50), nullable=True)
    contract_address = Column(String(100), nullable=True)
    launch_date = Column(DateTime, nullable=True)
    
    # Holder Information
    holder_count = Column(Integer, nullable=True)
    
    # Metadata
    image_url = Column(String(255), nullable=True)
    description = Column(String(2000), nullable=True)
    website = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_coin_rank', 'rank'),
        Index('idx_ath_distance', 'ath_distance_percent'),
        Index('idx_market_cap', 'market_cap'),
    )
    
    def __repr__(self):
        return f"<Coin {self.name} ({self.symbol})>"


class CoinData(Base):
    """
    Historical coin data for time-series analysis (TimescaleDB hypertable)
    """
    __tablename__ = "coin_data"
    
    id = Column(Integer, primary_key=True, index=True)
    coin_id = Column(String(100), nullable=False, index=True)
    
    # Time
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Price Data
    price = Column(Float, nullable=True)
    volume_24h = Column(Float, nullable=True)
    market_cap = Column(Float, nullable=True)
    
    # Technical Indicators
    rsi_14 = Column(Float, nullable=True)
    macd = Column(Float, nullable=True)
    macd_signal = Column(Float, nullable=True)
    ema_20 = Column(Float, nullable=True)
    ema_50 = Column(Float, nullable=True)
    sma_200 = Column(Float, nullable=True)
    bollinger_upper = Column(Float, nullable=True)
    bollinger_lower = Column(Float, nullable=True)
    atr_14 = Column(Float, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_coin_timestamp', 'coin_id', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<CoinData {self.coin_id} at {self.timestamp}>"
