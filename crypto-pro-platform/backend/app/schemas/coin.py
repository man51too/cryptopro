"""
Coin Pydantic Schemas
Defines data validation and serialization schemas for coins
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CoinBase(BaseModel):
    """Base schema for coin data"""
    coin_id: str
    symbol: str
    name: str
    
    class Config:
        from_attributes = True


class CoinResponse(CoinBase):
    """Complete coin response schema"""
    id: int
    market_cap_rank: Optional[int] = None
    current_price: Optional[float] = None
    market_cap: Optional[float] = None
    total_volume: Optional[float] = None
    
    # ATH Data
    ath: Optional[float] = None
    ath_date: Optional[datetime] = None
    ath_change_percentage: Optional[float] = None
    
    # Supply Data
    circulating_supply: Optional[float] = None
    total_supply: Optional[float] = None
    max_supply: Optional[float] = None
    
    # Additional Info
    description: Optional[str] = None
    website: Optional[str] = None
    blockchain: Optional[str] = None
    launch_date: Optional[datetime] = None
    holder_count: Optional[int] = None
    
    # Metadata
    is_active: bool = True
    last_updated: Optional[datetime] = None
    
    # Computed properties
    distance_from_ath: Optional[float] = None
    required_growth_to_ath: Optional[float] = None
    
    class Config:
        from_attributes = True


class CoinATHResponse(CoinBase):
    """Schema for ATH-focused coin data"""
    id: int
    current_price: Optional[float] = None
    ath: Optional[float] = None
    ath_date: Optional[datetime] = None
    ath_change_percentage: Optional[float] = None
    market_cap_rank: Optional[int] = None
    
    # Computed
    distance_from_ath: Optional[float] = None
    required_growth_to_ath: Optional[float] = None
    
    class Config:
        from_attributes = True


class CoinListResponse(BaseModel):
    """Paginated list of coins"""
    coins: List[CoinResponse]
    total: int
    skip: int
    limit: int


class CoinPriceDataSchema(BaseModel):
    """Schema for historical price data"""
    id: int
    coin_id: int
    timestamp: datetime
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: float
    timeframe: str = "1d"
    
    # Technical indicators
    rsi: Optional[float] = None
    macd: Optional[float] = None
    ema_20: Optional[float] = None
    sma_200: Optional[float] = None
    
    class Config:
        from_attributes = True
