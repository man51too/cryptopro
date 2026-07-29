"""
Dashboard API Endpoints
Provides endpoints for dashboard metrics and market overview
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import List, Dict
import logging

from ...core.database import get_db
from ...models.coin import Coin
from ...models.ai_prediction import AIPrediction

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/overview")
async def get_dashboard_overview(db: AsyncSession = Depends(get_db)):
    """
    Get comprehensive dashboard overview with key market metrics.
    """
    # Total active coins
    total_coins_query = select(func.count()).select_from(Coin).where(
        Coin.is_active == True
    )
    total_coins_result = await db.execute(total_coins_query)
    total_coins = total_coins_result.scalar()
    
    # Coins with ATH data
    coins_with_ath_query = select(func.count()).select_from(Coin).where(
        Coin.is_active == True,
        Coin.ath != None,
    )
    coins_with_ath_result = await db.execute(coins_with_ath_query)
    coins_with_ath = coins_with_ath_result.scalar()
    
    # Average distance from ATH
    avg_distance_query = select(func.avg(Coin.ath_change_percentage)).where(
        Coin.is_active == True,
        Coin.ath_change_percentage != None,
    )
    avg_distance_result = await db.execute(avg_distance_query)
    avg_distance_from_ath = avg_distance_result.scalar() or 0
    
    # Total AI predictions
    total_predictions_query = select(func.count()).select_from(AIPrediction).where(
        AIPrediction.is_active == True
    )
    total_predictions_result = await db.execute(total_predictions_query)
    total_predictions = total_predictions_result.scalar()
    
    # High score predictions count
    high_score_query = select(func.count()).select_from(AIPrediction).where(
        AIPrediction.is_active == True,
        AIPrediction.ai_recovery_score >= 75,
    )
    high_score_result = await db.execute(high_score_query)
    high_score_count = high_score_result.scalar()
    
    # Average AI score
    avg_score_query = select(func.avg(AIPrediction.ai_recovery_score)).where(
        AIPrediction.is_active == True
    )
    avg_score_result = await db.execute(avg_score_query)
    avg_ai_score = avg_score_result.scalar() or 0
    
    return {
        "market_stats": {
            "total_coins_tracked": total_coins,
            "coins_with_ath_data": coins_with_ath,
            "average_distance_from_ath": round(avg_distance_from_ath, 2),
        },
        "ai_stats": {
            "total_predictions": total_predictions,
            "high_score_predictions": high_score_count,
            "average_ai_score": round(avg_ai_score, 2),
        },
        "last_updated": func.now(),
    }


@router.get("/stats")
async def get_market_statistics(db: AsyncSession = Depends(get_db)):
    """
    Get detailed market statistics.
    """
    # Market cap distribution
    mc_distribution = {
        "large_cap": 0,  # Top 10
        "mid_cap": 0,    # 11-100
        "small_cap": 0,  # 101-500
        "micro_cap": 0,  # 501+
    }
    
    query = select(Coin.market_cap_rank).where(
        Coin.is_active == True,
        Coin.market_cap_rank != None,
    )
    result = await db.execute(query)
    ranks = result.scalars().all()
    
    for rank in ranks:
        if rank <= 10:
            mc_distribution["large_cap"] += 1
        elif rank <= 100:
            mc_distribution["mid_cap"] += 1
        elif rank <= 500:
            mc_distribution["small_cap"] += 1
        else:
            mc_distribution["micro_cap"] += 1
    
    # Risk level distribution
    risk_query = select(
        AIPrediction.risk_level,
        func.count()
    ).where(
        AIPrediction.is_active == True,
        AIPrediction.risk_level != None,
    ).group_by(AIPrediction.risk_level)
    
    risk_result = await db.execute(risk_query)
    risk_distribution = {row[0]: row[1] for row in risk_result.all()}
    
    return {
        "market_cap_distribution": mc_distribution,
        "risk_distribution": risk_distribution,
        "total_market_ranks": len(ranks),
    }


@router.get("/top-ai-picks")
async def get_top_ai_picks(db: AsyncSession = Depends(get_db)):
    """
    Get top AI picks for the dashboard.
    """
    query = select(AIPrediction, Coin).join(Coin).where(
        AIPrediction.is_active == True,
        Coin.is_active == True,
    )
    query = query.order_by(desc(AIPrediction.ai_recovery_score))
    query = query.limit(10)
    
    result = await db.execute(query)
    rows = result.all()
    
    picks = []
    for prediction, coin in rows:
        picks.append({
            "id": prediction.id,
            "coin_id": prediction.coin_id,
            "symbol": coin.symbol,
            "name": coin.name,
            "current_price": coin.current_price,
            "ai_score": prediction.ai_recovery_score,
            "recovery_probability": prediction.recovery_probability,
            "recommendation": prediction.recommendation,
            "risk_level": prediction.risk_level,
        })
    
    return {"picks": picks}


@router.get("/ath-opportunities")
async def get_ath_opportunities(db: AsyncSession = Depends(get_db)):
    """
    Get coins with best ATH recovery opportunities.
    """
    query = select(Coin).where(
        Coin.is_active == True,
        Coin.ath != None,
        Coin.current_price != None,
        Coin.ath_change_percentage < -50,  # At least 50% down from ATH
    )
    query = query.order_by(desc(Coin.ath_change_percentage))  # Biggest drops first
    query = query.limit(15)
    
    result = await db.execute(query)
    coins = result.scalars().all()
    
    opportunities = []
    for coin in coins:
        opportunities.append({
            "id": coin.id,
            "symbol": coin.symbol,
            "name": coin.name,
            "current_price": coin.current_price,
            "ath": coin.ath,
            "distance_from_ath": coin.ath_change_percentage,
            "required_growth": coin.required_growth_to_ath,
            "market_cap_rank": coin.market_cap_rank,
        })
    
    return {"opportunities": opportunities}
