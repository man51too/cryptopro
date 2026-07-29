"""
Dashboard API endpoints - Market overview and analytics
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.models.coin import Coin
from app.models.ai_prediction import AIPrediction


router = APIRouter()


# Pydantic schemas
class MarketOverview(BaseModel):
    total_coins: int
    coins_with_predictions: int
    average_ai_score: float
    high_score_count: int  # AI score >= 80
    market_sentiment: str  # Bullish, Bearish, Neutral
    top_gainers_count: int
    top_losers_count: int


class DashboardCoin(BaseModel):
    coin_id: str
    symbol: str
    name: str
    rank: int
    current_price: float
    ath_distance_percent: float
    ai_score: Optional[float] = None
    recovery_probability: Optional[float] = None
    risk_level: Optional[str] = None


class StatsResponse(BaseModel):
    total_market_cap: float
    total_volume_24h: float
    btc_dominance: Optional[float] = None
    eth_dominance: Optional[float] = None
    active_cryptocurrencies: int
    market_cap_change_24h: Optional[float] = None


@router.get("/overview", response_model=MarketOverview)
async def get_market_overview(db: Session = Depends(get_db)):
    """
    Get overall market overview
    """
    # Total coins
    total_coins = db.query(Coin).count()
    
    # Coins with predictions
    coins_with_predictions = db.query(AIPrediction).count()
    
    # Average AI score
    from sqlalchemy import func
    avg_result = db.query(func.avg(AIPrediction.ai_recovery_score)).first()
    average_ai_score = float(avg_result[0]) if avg_result[0] else 0
    
    # High score count
    high_score_count = db.query(AIPrediction).filter(
        AIPrediction.ai_recovery_score >= 80
    ).count()
    
    # Calculate market sentiment based on AI scores
    if average_ai_score >= 70:
        market_sentiment = "Bullish"
    elif average_ai_score <= 40:
        market_sentiment = "Bearish"
    else:
        market_sentiment = "Neutral"
    
    # Top gainers/losers (simplified - would need price history)
    top_gainers_count = 0
    top_losers_count = 0
    
    return MarketOverview(
        total_coins=total_coins,
        coins_with_predictions=coins_with_predictions,
        average_ai_score=round(average_ai_score, 2),
        high_score_count=high_score_count,
        market_sentiment=market_sentiment,
        top_gainers_count=top_gainers_count,
        top_losers_count=top_losers_count,
    )


@router.get("/stats", response_model=StatsResponse)
async def get_market_stats(db: Session = Depends(get_db)):
    """
    Get market statistics
    """
    from sqlalchemy import func
    
    # Total market cap
    total_market_cap_result = db.query(func.sum(Coin.market_cap)).first()
    total_market_cap = float(total_market_cap_result[0]) if total_market_cap_result[0] else 0
    
    # Total volume
    total_volume_result = db.query(func.sum(Coin.volume_24h)).first()
    total_volume_24h = float(total_volume_result[0]) if total_volume_result[0] else 0
    
    # Active cryptocurrencies
    active_cryptocurrencies = db.query(Coin).count()
    
    # BTC and ETH dominance (simplified)
    btc = db.query(Coin).filter(Coin.symbol == "BTC").first()
    eth = db.query(Coin).filter(Coin.symbol == "ETH").first()
    
    btc_dominance = None
    eth_dominance = None
    
    if btc and btc.market_cap and total_market_cap > 0:
        btc_dominance = round((btc.market_cap / total_market_cap) * 100, 2)
    
    if eth and eth.market_cap and total_market_cap > 0:
        eth_dominance = round((eth.market_cap / total_market_cap) * 100, 2)
    
    return StatsResponse(
        total_market_cap=total_market_cap,
        total_volume_24h=total_volume_24h,
        btc_dominance=btc_dominance,
        eth_dominance=eth_dominance,
        active_cryptocurrencies=active_cryptocurrencies,
        market_cap_change_24h=None,  # Would need historical data
    )


@router.get("/top-ai-picks", response_model=List[DashboardCoin])
async def get_top_ai_picks(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get top AI-recommended coins
    """
    # Get top AI predictions
    predictions = db.query(AIPrediction).order_by(
        AIPrediction.ai_recovery_score.desc()
    ).limit(limit).all()
    
    results = []
    for pred in predictions:
        coin = db.query(Coin).filter(Coin.coin_id == pred.coin_id).first()
        if coin:
            results.append(DashboardCoin(
                coin_id=coin.coin_id,
                symbol=coin.symbol,
                name=coin.name,
                rank=coin.rank or 0,
                current_price=coin.current_price or 0,
                ath_distance_percent=coin.ath_distance_percent or 0,
                ai_score=pred.ai_recovery_score,
                recovery_probability=pred.recovery_probability,
                risk_level=pred.risk_level,
            ))
    
    return results


@router.get("/ath-opportunities", response_model=List[DashboardCoin])
async def get_ath_opportunities(
    limit: int = Query(20, ge=1, le=100),
    min_ai_score: float = Query(60, ge=0, le=100),
    db: Session = Depends(get_db)
):
    """
    Get coins with best ATH recovery opportunities (high distance + good AI score)
    """
    # Get coins with significant ATH distance and good AI scores
    coins = db.query(Coin).join(
        AIPrediction, Coin.coin_id == AIPrediction.coin_id
    ).filter(
        Coin.ath_distance_percent < -50,  # At least 50% below ATH
        AIPrediction.ai_recovery_score >= min_ai_score
    ).order_by(
        Coin.ath_distance_percent.asc(),  # Biggest drops first
        AIPrediction.ai_recovery_score.desc()  # Then by AI score
    ).limit(limit).all()
    
    results = []
    for coin in coins:
        pred = db.query(AIPrediction).filter(
            AIPrediction.coin_id == coin.coin_id
        ).first()
        
        results.append(DashboardCoin(
            coin_id=coin.coin_id,
            symbol=coin.symbol,
            name=coin.name,
            rank=coin.rank or 0,
            current_price=coin.current_price or 0,
            ath_distance_percent=coin.ath_distance_percent or 0,
            ai_score=pred.ai_recovery_score if pred else None,
            recovery_probability=pred.recovery_probability if pred else None,
            risk_level=pred.risk_level if pred else None,
        ))
    
    return results
