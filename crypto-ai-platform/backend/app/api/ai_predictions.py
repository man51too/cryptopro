"""
AI Predictions API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.models.ai_prediction import AIPrediction


router = APIRouter()


# Pydantic schemas
class AIPredictionResponse(BaseModel):
    coin_id: str
    ai_recovery_score: float
    recovery_probability: float
    estimated_recovery_months_min: Optional[float] = None
    estimated_recovery_months_max: Optional[float] = None
    risk_level: Optional[str] = None
    technical_score: Optional[float] = None
    fundamental_score: Optional[float] = None
    onchain_score: Optional[float] = None
    sentiment_score: Optional[float] = None
    historical_score: Optional[float] = None
    analysis_reasons: Optional[str] = None
    bullish_signals: Optional[str] = None
    bearish_signals: Optional[str] = None
    confidence_level: Optional[float] = None
    
    class Config:
        from_attributes = True


class MoonshotCandidate(BaseModel):
    rank: int
    coin_id: str
    symbol: str
    name: str
    current_price: float
    ath: float
    ai_score: float
    recovery_probability: float
    estimated_time_min: Optional[float] = None
    estimated_time_max: Optional[float] = None
    risk_level: Optional[str] = None
    reasons: List[str] = []


@router.get("/predictions", response_model=List[AIPredictionResponse])
async def get_predictions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    min_score: Optional[float] = Query(None, ge=0, le=100),
    db: Session = Depends(get_db)
):
    """
    Get AI predictions for coins
    """
    query = db.query(AIPrediction)
    
    if min_score is not None:
        query = query.filter(AIPrediction.ai_recovery_score >= min_score)
    
    predictions = query.offset(skip).limit(limit).all()
    return predictions


@router.get("/prediction/{coin_id}", response_model=AIPredictionResponse)
async def get_prediction(coin_id: str, db: Session = Depends(get_db)):
    """
    Get AI prediction for a specific coin
    """
    prediction = db.query(AIPrediction).filter(
        AIPrediction.coin_id == coin_id
    ).first()
    
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    return prediction


@router.get("/moonshot", response_model=List[MoonshotCandidate])
async def get_moonshot_candidates(
    limit: int = Query(20, ge=1, le=100),
    min_score: float = Query(70, ge=0, le=100),
    db: Session = Depends(get_db)
):
    """
    Get top AI moonshot candidates - coins most likely to return to ATH soon
    """
    from app.models.coin import Coin
    
    # Join with Coin model to get coin details
    predictions = db.query(AIPrediction).join(
        Coin, AIPrediction.coin_id == Coin.coin_id
    ).filter(
        AIPrediction.ai_recovery_score >= min_score
    ).order_by(
        AIPrediction.ai_recovery_score.desc()
    ).limit(limit).all()
    
    results = []
    for idx, pred in enumerate(predictions, 1):
        coin = db.query(Coin).filter(Coin.coin_id == pred.coin_id).first()
        
        # Parse reasons from text
        reasons = []
        if pred.analysis_reasons:
            import json
            try:
                reasons = json.loads(pred.analysis_reasons)
            except:
                reasons = [pred.analysis_reasons]
        
        results.append(MoonshotCandidate(
            rank=idx,
            coin_id=pred.coin_id,
            symbol=coin.symbol if coin else "N/A",
            name=coin.name if coin else "N/A",
            current_price=coin.current_price if coin else 0,
            ath=coin.ath if coin else 0,
            ai_score=pred.ai_recovery_score or 0,
            recovery_probability=pred.recovery_probability or 0,
            estimated_time_min=pred.estimated_recovery_months_min,
            estimated_time_max=pred.estimated_recovery_months_max,
            risk_level=pred.risk_level,
            reasons=reasons,
        ))
    
    return results


@router.get("/scores/high", response_model=List[AIPredictionResponse])
async def get_high_score_predictions(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """
    Get predictions with high AI scores (>= 80)
    """
    predictions = db.query(AIPrediction).filter(
        AIPrediction.ai_recovery_score >= 80
    ).order_by(
        AIPrediction.ai_recovery_score.desc()
    ).limit(limit).all()
    
    return predictions


@router.get("/risk/{risk_level}", response_model=List[AIPredictionResponse])
async def get_predictions_by_risk(
    risk_level: str,
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get predictions filtered by risk level
    """
    valid_levels = ["Low", "Medium", "High", "Very High"]
    if risk_level not in valid_levels:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid risk level. Must be one of: {valid_levels}"
        )
    
    predictions = db.query(AIPrediction).filter(
        AIPrediction.risk_level == risk_level
    ).limit(limit).all()
    
    return predictions
