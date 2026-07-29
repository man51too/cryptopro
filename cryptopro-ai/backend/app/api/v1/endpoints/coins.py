"""
Coins API endpoints for cryptocurrency data and ATH analysis.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.coin import Coin
from app.schemas.coin import (
    Coin as CoinSchema,
    CoinListResponse,
    ATHDistanceResponse,
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=CoinListResponse)
async def list_coins(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    search: Optional[str] = None,
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
):
    """
    List all cryptocurrencies with pagination.
    
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 50, max: 200)
    - **search**: Search by name or symbol
    - **active_only**: Filter only active coins
    """
    query = select(Coin)
    
    if active_only:
        query = query.where(Coin.is_active == True)
    
    if search:
        search_filter = f"%{search.upper()}%"
        query = query.where(
            (func.upper(Coin.name).like(search_filter)) |
            (func.upper(Coin.symbol).like(search_filter))
        )
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Apply pagination
    offset = (page - 1) * page_size
    query = query.order_by(Coin.rank).offset(offset).limit(page_size)
    
    result = await db.execute(query)
    coins = result.scalars().all()
    
    return {
        "items": coins,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size,
    }


@router.get("/{coin_id}", response_model=CoinSchema)
async def get_coin(
    coin_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get detailed information about a specific cryptocurrency."""
    result = await db.execute(select(Coin).where(Coin.id == coin_id))
    coin = result.scalar_one_or_none()
    
    if not coin:
        raise HTTPException(
            status_code=404,
            detail=f"Coin with id {coin_id} not found",
        )
    
    return coin


@router.get("/symbol/{symbol}", response_model=CoinSchema)
async def get_coin_by_symbol(
    symbol: str,
    db: AsyncSession = Depends(get_db),
):
    """Get coin information by symbol."""
    result = await db.execute(
        select(Coin).where(func.upper(Coin.symbol) == symbol.upper())
    )
    coin = result.scalar_one_or_none()
    
    if not coin:
        raise HTTPException(
            status_code=404,
            detail=f"Coin with symbol {symbol} not found",
        )
    
    return coin


@router.get("/ath/distance", response_model=List[ATHDistanceResponse])
async def get_coins_by_ath_distance(
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
):
    """
    Get coins sorted by distance from All-Time High.
    
    Returns coins with the largest drop from ATH first.
    """
    query = select(Coin).where(
        Coin.ath_price.isnot(None),
        Coin.current_price.isnot(None),
        Coin.current_price > 0,
    )
    
    if active_only:
        query = query.where(Coin.is_active == True)
    
    # Calculate distance and order by it
    query = query.order_by(
        ((Coin.current_price - Coin.ath_price) / Coin.ath_price).asc()
    ).limit(limit)
    
    result = await db.execute(query)
    coins = result.scalars().all()
    
    # Format response with ranking
    responses = []
    for rank, coin in enumerate(coins, 1):
        distance = ((coin.current_price - coin.ath_price) / coin.ath_price) * 100
        required_growth = coin.ath_price / coin.current_price if coin.current_price else 0
        
        responses.append(
            ATHDistanceResponse(
                coin_id=coin.id,
                symbol=coin.symbol,
                name=coin.name,
                current_price=coin.current_price,
                ath_price=coin.ath_price,
                ath_date=coin.ath_date,
                distance_percent=distance,
                required_growth_multiple=required_growth,
                rank_by_distance=rank,
            )
        )
    
    return responses


@router.get("/top/{count}", response_model=List[CoinSchema])
async def get_top_coins(
    count: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """Get top N coins by market cap rank."""
    result = await db.execute(
        select(Coin)
        .where(Coin.is_active == True)
        .order_by(Coin.rank)
        .limit(count)
    )
    coins = result.scalars().all()
    return coins


@router.get("/search", response_model=List[CoinSchema])
async def search_coins(
    q: str = Query(..., min_length=2),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Search coins by name or symbol."""
    search_term = f"%{q.upper()}%"
    result = await db.execute(
        select(Coin)
        .where(
            (func.upper(Coin.name).like(search_term)) |
            (func.upper(Coin.symbol).like(search_term))
        )
        .limit(limit)
    )
    return result.scalars().all()
