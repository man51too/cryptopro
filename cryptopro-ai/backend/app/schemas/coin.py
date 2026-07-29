"""Pydantic schemas for coin-related data."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


class CoinBase(BaseModel):
    """Base coin schema."""
    
    symbol: str = Field(..., max_length=20)
    name: str = Field(..., max_length=100)
    coingecko_id: Optional[str] = None
    coinmarketcap_id: Optional[str] = None


class CoinCreate(CoinBase):
    """Schema for creating a coin."""
    
    pass


class CoinUpdate(BaseModel):
    """Schema for updating a coin."""
    
    name: Optional[str] = None
    coingecko_id: Optional[str] = None
    coinmarketcap_id: Optional[str] = None
    is_active: Optional[bool] = None


class CoinInDB(CoinBase):
    """Schema for coin in database."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    rank: int = 0
    market_cap_usd: Optional[float] = None
    volume_24h_usd: Optional[float] = None
    circulating_supply: Optional[float] = None
    total_supply: Optional[float] = None
    max_supply: Optional[float] = None
    ath_price: Optional[float] = None
    ath_date: Optional[datetime] = None
    atl_price: Optional[float] = None
    atl_date: Optional[datetime] = None
    price_change_24h: Optional[float] = None
    price_change_percentage_24h: Optional[float] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


class Coin(CoinInDB):
    """Public coin schema."""
    
    current_price: Optional[float] = None
    ath_distance_percent: Optional[float] = None
    required_growth_multiple: Optional[float] = None


class CoinPriceData(BaseModel):
    """Schema for coin price data."""
    
    coin_id: int
    price_usd: float
    market_cap_usd: Optional[float] = None
    volume_24h_usd: Optional[float] = None
    price_change_24h: Optional[float] = None
    timestamp: datetime


class CoinWithPrediction(Coin):
    """Coin schema with AI prediction."""
    
    ai_score: Optional[float] = None
    recovery_probability: Optional[float] = None
    estimated_months_to_ath: Optional[int] = None
    risk_level: Optional[str] = None


class ATHDistanceResponse(BaseModel):
    """Response for ATH distance analysis."""
    
    coin_id: int
    symbol: str
    name: str
    current_price: float
    ath_price: float
    ath_date: Optional[datetime]
    distance_percent: float
    required_growth_multiple: float
    rank_by_distance: int


class CoinListResponse(BaseModel):
    """Paginated coin list response."""
    
    items: List[Coin]
    total: int
    page: int
    page_size: int
    pages: int
