"""
AI Predictions API Endpoints
Provides endpoints for AI-powered predictions and analysis
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_
from typing import List, Optional
import logging

from ...core.database import get_db
from ...models.ai_prediction import AIPrediction, AIRecoveryScore
from ...models.coin import Coin
from ...schemas.ai_prediction import (
    AIPredictionResponse,
    MoonshotCandidateResponse,
    AIScoreResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/predictions", response_model=List[AIPredictionResponse])
async def get_ai_predictions(
    limit: int = Query(50, ge=1, le=500),
    min_score: Optional[float] = Query(None, ge=0, le=100),
    coin_id: Optional[int] = Query(None, ge=1),
    db: AsyncSession = Depends(get_db),
):
    """
    Get AI predictions for cryptocurrencies.
    
    Returns comprehensive AI analysis including recovery probability,
    risk assessment, and detailed breakdown.
    """
    query = select(AIPrediction).join(Coin).where(
        AIPrediction.is_active == True,
        Coin.is_active == True,
    )
    
    if coin_id:
        query = query.where(AIPrediction.coin_id == coin_id)
    
    if min_score is not None:
        query = query.where(AIPrediction.ai_recovery_score >= min_score)
    
    query = query.order_by(desc(AIPrediction.ai_recovery_score))
    query = query.limit(limit)
    
    result = await db.execute(query)
    predictions = result.scalars().all()
    
    return [AIPredictionResponse.from_orm(p) for p in predictions]


@router.get("/prediction/{coin_id}", response_model=AIPredictionResponse)
async def get_coin_prediction(coin_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get AI prediction for a specific cryptocurrency.
    """
    query = select(AIPrediction).where(
        AIPrediction.coin_id == coin_id,
        AIPrediction.is_active == True,
    )
    query = query.order_by(desc(AIPrediction.prediction_date))
    
    result = await db.execute(query)
    prediction = result.scalar_one_or_none()
    
    if not prediction:
        raise HTTPException(status_code=404, detail="No prediction found for this coin")
    
    return AIPredictionResponse.from_orm(prediction)


@router.get("/moonshot", response_model=List[MoonshotCandidateResponse])
async def get_moonshot_candidates(
    limit: int = Query(20, ge=1, le=100),
    min_ai_score: float = Query(70, ge=50, le=100),
    max_distance_from_ath: float = Query(80, ge=50, le=95),
    db: AsyncSession = Depends(get_db),
):
    """
    Get top moonshot candidates - coins most likely to return to ATH soon.
    
    Filters for:
    - High AI Recovery Score
    - Reasonable distance from ATH
    - Strong fundamentals and technicals
    """
    query = select(AIPrediction, Coin).join(Coin).where(
        AIPrediction.is_active == True,
        Coin.is_active == True,
        AIPrediction.ai_recovery_score >= min_ai_score,
        Coin.ath_change_percentage <= -max_distance_from_ath * -1,  # Convert to negative
        Coin.ath_change_percentage >= -100,  # Valid range
    )
    
    query = query.order_by(desc(AIPrediction.ai_recovery_score))
    query = query.limit(limit)
    
    result = await db.execute(query)
    rows = result.all()
    
    candidates = []
    for prediction, coin in rows:
        candidates.append(MoonshotCandidateResponse(
            id=prediction.id,
            coin_id=prediction.coin_id,
            symbol=coin.symbol,
            name=coin.name,
            current_price=coin.current_price,
            ath=coin.ath,
            distance_from_ath=coin.ath_change_percentage,
            required_growth_to_ath=coin.required_growth_to_ath,
            ai_recovery_score=prediction.ai_recovery_score,
            recovery_probability=prediction.recovery_probability,
            estimated_recovery_months=prediction.estimated_recovery_months,
            risk_level=prediction.risk_level,
            recommendation=prediction.recommendation,
            reasons=prediction.analysis_reasons or [],
        ))
    
    return candidates


@router.get("/scores/high", response_model=List[AIScoreResponse])
async def get_high_score_predictions(
    limit: int = Query(30, ge=1, le=200),
    min_score: float = Query(75, ge=60, le=100),
    db: AsyncSession = Depends(get_db),
):
    """
    Get predictions with the highest AI scores.
    """
    query = select(AIPrediction, Coin).join(Coin).where(
        AIPrediction.is_active == True,
        Coin.is_active == True,
        AIPrediction.ai_recovery_score >= min_score,
    )
    
    query = query.order_by(desc(AIPrediction.ai_recovery_score))
    query = query.limit(limit)
    
    result = await db.execute(query)
    rows = result.all()
    
    return [
        AIScoreResponse(
            id=p.id,
            coin_id=p.coin_id,
            symbol=c.symbol,
            name=c.name,
            ai_recovery_score=p.ai_recovery_score,
            recovery_probability=p.recovery_probability,
            technical_score=p.technical_score,
            fundamental_score=p.fundamental_score,
            onchain_score=p.onchain_score,
            sentiment_score=p.sentiment_score,
            historical_score=p.historical_score,
            recommendation=p.recommendation,
        )
        for p, c in rows
    ]


@router.get("/summary")
async def get_ai_summary(db: AsyncSession = Depends(get_db)):
    """
    Get summary statistics of AI predictions.
    """
    # Total predictions
    total_query = select(func.count()).select_from(AIPrediction).where(
        AIPrediction.is_active == True
    )
    total_result = await db.execute(total_query)
    total_predictions = total_result.scalar()
    
    # Average score
    avg_query = select(func.avg(AIPrediction.ai_recovery_score)).where(
        AIPrediction.is_active == True
    )
    avg_result = await db.execute(avg_query)
    avg_score = avg_result.scalar() or 0
    
    # High confidence predictions (score >= 75)
    high_conf_query = select(func.count()).select_from(AIPrediction).where(
        AIPrediction.is_active == True,
        AIPrediction.ai_recovery_score >= 75,
    )
    high_conf_result = await db.execute(high_conf_query)
    high_confidence_count = high_conf_result.scalar()
    
    # By risk level
    risk_query = select(
        AIPrediction.risk_level,
        func.count()
    ).where(
        AIPrediction.is_active == True
    ).group_by(AIPrediction.risk_level)
    
    risk_result = await db.execute(risk_query)
    risk_distribution = {row[0]: row[1] for row in risk_result.all()}
    
    return {
        "total_predictions": total_predictions,
        "average_ai_score": round(avg_score, 2),
        "high_confidence_count": high_confidence_count,
        "risk_distribution": risk_distribution,
        "last_updated": func.now(),
    }
