"""
Coins API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.models.coin import Coin


router = APIRouter()


# Pydantic schemas
class CoinBase(BaseModel):
    coin_id: str
    symbol: str
    name: str
    rank: Optional[int] = None
    current_price: Optional[float] = None
    ath: Optional[float] = None
    market_cap: Optional[float] = None
    volume_24h: Optional[float] = None


class CoinResponse(CoinBase):
    id: int
    ath_distance_percent: Optional[float] = None
    required_growth_multiplier: Optional[float] = None
    
    class Config:
        from_attributes = True


class ATHDistanceResponse(BaseModel):
    rank: int
    coin_id: str
    symbol: str
    name: str
    current_price: float
    ath: float
    ath_distance_percent: float
    required_growth_multiplier: float
    market_cap: Optional[float] = None
    volume_24h: Optional[float] = None


@router.get("/", response_model=List[CoinResponse])
async def get_coins(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get list of cryptocurrencies
    """
    coins = db.query(Coin).offset(skip).limit(limit).all()
    return coins


@router.get("/{coin_id}", response_model=CoinResponse)
async def get_coin(coin_id: str, db: Session = Depends(get_db)):
    """
    Get specific cryptocurrency by ID
    """
    coin = db.query(Coin).filter(Coin.coin_id == coin_id).first()
    if not coin:
        raise HTTPException(status_code=404, detail="Coin not found")
    return coin


@router.get("/ath/distance", response_model=List[ATHDistanceResponse])
async def get_coins_by_ath_distance(
    limit: int = Query(100, ge=1, le=1000),
    min_distance: Optional[float] = Query(None, description="Minimum ATH distance percentage"),
    db: Session = Depends(get_db)
):
    """
    Get coins sorted by ATH distance (biggest drop from ATH first)
    """
    query = db.query(Coin).filter(
        Coin.ath_distance_percent.isnot(None)
    )
    
    if min_distance is not None:
        query = query.filter(Coin.ath_distance_percent <= min_distance)
    
    coins = query.order_by(Coin.ath_distance_percent.asc()).limit(limit).all()
    
    results = []
    for idx, coin in enumerate(coins, 1):
        results.append(ATHDistanceResponse(
            rank=idx,
            coin_id=coin.coin_id,
            symbol=coin.symbol,
            name=coin.name,
            current_price=coin.current_price or 0,
            ath=coin.ath or 0,
            ath_distance_percent=coin.ath_distance_percent or 0,
            required_growth_multiplier=coin.required_growth_multiplier or 0,
            market_cap=coin.market_cap,
            volume_24h=coin.volume_24h,
        ))
    
    return results


@router.get("/search", response_model=List[CoinResponse])
async def search_coins(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Search coins by name or symbol
    """
    coins = db.query(Coin).filter(
        (Coin.name.ilike(f"%{q}%")) | 
        (Coin.symbol.ilike(f"%{q}%"))
    ).limit(limit).all()
    return coins


@router.get("/top/{count}", response_model=List[CoinResponse])
async def get_top_coins(count: int = Query(100, ge=1, le=1000), db: Session = Depends(get_db)):
    """
    Get top N coins by market cap rank
    """
    coins = db.query(Coin).order_by(Coin.rank.asc()).limit(count).all()
    return coins
