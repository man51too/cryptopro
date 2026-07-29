"""
Coins API Endpoints
Provides endpoints for cryptocurrency data and ATH analysis
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import List, Optional
import logging

from ...core.database import get_db
from ...models.coin import Coin, CoinPriceData
from ...schemas.coin import CoinResponse, CoinATHResponse, CoinListResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=CoinListResponse)
async def get_coins(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=1000, description="Maximum number of records to return"),
    search: Optional[str] = Query(None, description="Search by name or symbol"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get list of cryptocurrencies.
    
    Returns paginated list of coins with optional search filtering.
    """
    query = select(Coin).where(Coin.is_active == True)
    
    if search:
        search_filter = f"%{search.upper()}%"
        query = query.where(
            (Coin.name.ilike(search_filter)) | 
            (Coin.symbol.ilike(search_filter))
        )
    
    query = query.order_by(Coin.market_cap_rank)\n    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    coins = result.scalars().all()
    
    # Get total count
    count_query = select(func.count()).select_from(Coin).where(Coin.is_active == True)
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    return {
        "coins": [CoinResponse.from_orm(c) for c in coins],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/{coin_id}", response_model=CoinResponse)
async def get_coin(coin_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get detailed information about a specific cryptocurrency.
    """
    query = select(Coin).where(Coin.id == coin_id)
    result = await db.execute(query)
    coin = result.scalar_one_or_none()
    
    if not coin:
        raise HTTPException(status_code=404, detail="Coin not found")
    
    return CoinResponse.from_orm(coin)


@router.get("/symbol/{symbol}", response_model=CoinResponse)
async def get_coin_by_symbol(symbol: str, db: AsyncSession = Depends(get_db)):
    """
    Get coin information by symbol (e.g., BTC, ETH).
    """
    query = select(Coin).where(Coin.symbol == symbol.upper())
    result = await db.execute(query)
    coin = result.scalar_one_or_none()
    
    if not coin:
        raise HTTPException(status_code=404, detail="Coin not found")
    
    return CoinResponse.from_orm(coin)


@router.get("/ath/distance", response_model=List[CoinATHResponse])
async def get_coins_by_ath_distance(
    limit: int = Query(100, ge=1, le=1000, description="Number of coins to return"),
    min_distance: Optional[float] = Query(None, description="Minimum distance from ATH (%)"),
    max_distance: Optional[float] = Query(None, description="Maximum distance from ATH (%)"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get coins sorted by distance from All-Time High.
    
    Shows coins with the biggest drop from their ATH - potential recovery candidates.
    """
    query = select(Coin).where(
        Coin.is_active == True,
        Coin.ath != None,
        Coin.current_price != None,
    )
    
    if min_distance is not None:
        query = query.where(Coin.ath_change_percentage <= min_distance)
    
    if max_distance is not None:
        query = query.where(Coin.ath_change_percentage >= max_distance)
    
    # Order by distance from ATH (biggest drops first)
    query = query.order_by(desc(Coin.ath_change_percentage))
    query = query.limit(limit)
    
    result = await db.execute(query)
    coins = result.scalars().all()
    
    return [CoinATHResponse.from_orm(c) for c in coins]


@router.get("/top/{count}", response_model=List[CoinResponse])
async def get_top_coins(count: int, db: AsyncSession = Depends(get_db)):
    """
    Get top N cryptocurrencies by market cap rank.
    """
    if count < 1 or count > 1000:
        raise HTTPException(status_code=400, detail="Count must be between 1 and 1000")
    
    query = select(Coin).where(Coin.is_active == True)
    query = query.order_by(Coin.market_cap_rank)
    query = query.limit(count)
    
    result = await db.execute(query)
    coins = result.scalars().all()
    
    return [CoinResponse.from_orm(c) for c in coins]


@router.get("/gainers", response_model=List[CoinResponse])
async def get_top_gainers(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """
    Get top gaining cryptocurrencies (24h price change).
    """
    # This would require price change data - placeholder for now
    query = select(Coin).where(Coin.is_active == True)
    query = query.order_by(desc(Coin.ath_change_percentage))
    query = query.limit(limit)
    
    result = await db.execute(query)
    coins = result.scalars().all()
    
    return [CoinResponse.from_orm(c) for c in coins]


@router.get("/losers", response_model=List[CoinResponse])
async def get_top_losers(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """
    Get top losing cryptocurrencies (24h price change).
    """
    query = select(Coin).where(Coin.is_active == True)
    query = query.order_by(Coin.ath_change_percentage)
    query = query.limit(limit)
    
    result = await db.execute(query)
    coins = result.scalars().all()
    
    return [CoinResponse.from_orm(c) for c in coins]
