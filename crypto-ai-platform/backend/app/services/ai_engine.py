"""
AI Engine - Main prediction engine using ensemble ML models
"""
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from loguru import logger

from app.core.config import settings
from app.services.technical_analysis import technical_analysis_service


class AIRecoveryEngine:
    """
    AI Engine for predicting cryptocurrency ATH recovery probability
    
    Uses ensemble of:
    - Technical Analysis (30%)
    - Fundamental Analysis (25%)
    - On-chain Analysis (20%)
    - Market Sentiment (15%)
    - Historical Patterns (10%)
    """
    
    def __init__(self):
        self.model_version = "1.0.0"
        
        # Scoring weights from config
        self.weights = {
            "technical": settings.TECHNICAL_WEIGHT,
            "fundamental": settings.FUNDAMENTAL_WEIGHT,
            "onchain": settings.ONCHAIN_WEIGHT,
            "sentiment": settings.SENTIMENT_WEIGHT,
            "historical": settings.HISTORICAL_WEIGHT,
        }
    
    def calculate_fundamental_score(self, coin_data: Dict[str, Any]) -> float:
        """
        Calculate fundamental analysis score (0-100)
        
        Factors:
        - Market Cap rank
        - Volume/MCap ratio
        - Supply metrics
        - Development activity (if available)
        """
        score = 50.0  # Base score
        
        # Market Cap Rank scoring
        rank = coin_data.get("rank") or coin_data.get("market_cap_rank")
        if rank:
            if rank <= 10:
                score += 20
            elif rank <= 50:
                score += 15
            elif rank <= 100:
                score += 10
            elif rank <= 500:
                score += 5
        
        # Volume/MarketCap ratio (liquidity)
        volume_24h = coin_data.get("volume_24h") or 0
        market_cap = coin_data.get("market_cap") or 1
        
        if market_cap > 0:
            vol_mcap_ratio = volume_24h / market_cap
            if vol_mcap_ratio > 0.1:  # High liquidity
                score += 15
            elif vol_mcap_ratio > 0.05:
                score += 10
            elif vol_mcap_ratio > 0.02:
                score += 5
        
        # Supply metrics
        circulating_supply = coin_data.get("circulating_supply") or 0
        max_supply = coin_data.get("max_supply") or 0
        
        if max_supply > 0 and circulating_supply > 0:
            supply_ratio = circulating_supply / max_supply
            if supply_ratio > 0.9:  # Most tokens already in circulation
                score += 10
            elif supply_ratio > 0.7:
                score += 5
        
        return min(100, max(0, score))
    
    def calculate_onchain_score(self, coin_data: Dict[str, Any]) -> float:
        """
        Calculate on-chain analysis score (0-100)
        
        Note: In production, this would integrate with Glassnode, Santiment APIs
        For now, uses proxy metrics from available data
        """
        score = 50.0  # Base score
        
        # Holder count (if available)
        holder_count = coin_data.get("holder_count")
        if holder_count:
            if holder_count > 1000000:
                score += 25
            elif holder_count > 100000:
                score += 20
            elif holder_count > 10000:
                score += 15
            elif holder_count > 1000:
                score += 10
        
        # Transaction volume proxy (using 24h volume)
        volume_24h = coin_data.get("volume_24h") or 0
        if volume_24h > 100_000_000:  # $100M+
            score += 20
        elif volume_24h > 10_000_000:  # $10M+
            score += 15
        elif volume_24h > 1_000_000:  # $1M+
            score += 10
        
        return min(100, max(0, score))
    
    def calculate_sentiment_score(self, coin_data: Dict[str, Any]) -> float:
        """
        Calculate market sentiment score (0-100)
        
        Note: In production, would integrate with LunarCrush, social media APIs
        For now, uses price momentum as proxy
        """
        score = 50.0  # Base score
        
        # Price change proxy (would use actual sentiment data in production)
        ath_distance = coin_data.get("ath_distance_percent") or 0
        
        # Coins very far from ATH might have negative sentiment
        if ath_distance > -30:  # Close to ATH
            score += 20
        elif ath_distance > -50:
            score += 10
        elif ath_distance < -90:  # Very far, potential oversold
            score += 15  # Contrarian signal
        
        # Volume trend proxy
        volume_24h = coin_data.get("volume_24h") or 0
        if volume_24h > 50_000_000:
            score += 15  # High volume suggests interest
        
        return min(100, max(0, score))
    
    def calculate_historical_score(self, coin_data: Dict[str, Any]) -> float:
        """
        Calculate historical pattern score (0-100)
        
        Analyzes historical recovery patterns
        """
        score = 50.0  # Base score
        
        # ATH distance analysis
        ath_distance = coin_data.get("ath_distance_percent") or 0
        required_growth = coin_data.get("required_growth_multiplier") or 1
        
        # Moderate distances often recover better than extreme ones
        if -60 <= ath_distance <= -30:
            score += 25  # Sweet spot for recovery
        elif -80 <= ath_distance < -60:
            score += 15
        elif ath_distance > -30:
            score += 10  # Already near ATH
        elif ath_distance < -90:
            score += 20  # Deep value play (high risk, high reward)
        
        # Age of coin (older coins more likely to recover)
        launch_date = coin_data.get("launch_date")
        if launch_date:
            try:
                age_days = (datetime.utcnow() - launch_date).days
                if age_days > 1000:  # ~3 years
                    score += 15
                elif age_days > 365:  # ~1 year
                    score += 10
            except:
                pass
        
        return min(100, max(0, score))
    
    def calculate_recovery_probability(
        self,
        ai_score: float,
        ath_distance: float,
        risk_level: str
    ) -> float:
        """
        Calculate probability of returning to ATH (0-100%)
        
        Based on AI score, ATH distance, and risk assessment
        """
        # Base probability from AI score
        base_prob = ai_score * 0.9  # Scale down slightly
        
        # Adjust for ATH distance
        if ath_distance > -40:
            distance_factor = 1.1  # Easier to recover
        elif ath_distance > -70:
            distance_factor = 1.0  # Neutral
        else:
            distance_factor = 0.85  # Harder to recover
        
        # Adjust for risk level
        risk_multipliers = {
            "Low": 1.15,
            "Medium": 1.0,
            "High": 0.85,
            "Very High": 0.7,
        }
        risk_factor = risk_multipliers.get(risk_level, 1.0)
        
        probability = base_prob * distance_factor * risk_factor
        
        return min(95, max(5, probability))  # Clamp between 5-95%
    
    def estimate_recovery_time(
        self,
        ai_score: float,
        ath_distance: float,
        risk_level: str
    ) -> Tuple[float, float]:
        """
        Estimate time range (in months) for ATH recovery
        """
        # Base estimate from AI score
        if ai_score >= 80:
            base_months = 3
        elif ai_score >= 60:
            base_months = 6
        elif ai_score >= 40:
            base_months = 12
        else:
            base_months = 24
        
        # Adjust for ATH distance
        distance_factor = abs(ath_distance) / 50  # Normalize
        adjusted_months = base_months * (1 + distance_factor)
        
        # Risk adjustment
        risk_multipliers = {
            "Low": 0.8,
            "Medium": 1.0,
            "High": 1.3,
            "Very High": 1.6,
        }
        risk_factor = risk_multipliers.get(risk_level, 1.0)
        
        final_months = adjusted_months * risk_factor
        
        # Return range
        min_months = max(1, round(final_months * 0.7, 1))
        max_months = round(final_months * 1.5, 1)
        
        return min_months, max_months
    
    def determine_risk_level(
        self,
        ai_score: float,
        volatility: Optional[float] = None,
        market_cap_rank: Optional[int] = None
    ) -> str:
        """
        Determine risk level: Low, Medium, High, Very High
        """
        risk_score = 0
        
        # AI score factor (lower score = higher risk)
        if ai_score < 40:
            risk_score += 40
        elif ai_score < 60:
            risk_score += 25
        elif ai_score < 80:
            risk_score += 10
        
        # Market cap rank factor
        if market_cap_rank:
            if market_cap_rank > 500:
                risk_score += 30
            elif market_cap_rank > 100:
                risk_score += 20
            elif market_cap_rank > 50:
                risk_score += 10
        
        # Determine level
        if risk_score >= 60:
            return "Very High"
        elif risk_score >= 40:
            return "High"
        elif risk_score >= 20:
            return "Medium"
        else:
            return "Low"
    
    def generate_analysis_reasons(
        self,
        technical_score: float,
        fundamental_score: float,
        onchain_score: float,
        sentiment_score: float,
        coin_data: Dict[str, Any]
    ) -> List[str]:
        """Generate human-readable analysis reasons"""
        reasons = []
        
        # Technical reasons
        if technical_score >= 70:
            reasons.append("Strong technical indicators")
        elif technical_score >= 50:
            reasons.append("Neutral technical setup")
        else:
            reasons.append("Weak technical signals")
        
        # Fundamental reasons
        if fundamental_score >= 70:
            reasons.append("Strong fundamentals")
            reasons.append("Solid market position")
        
        # On-chain reasons
        if onchain_score >= 70:
            reasons.append("Positive on-chain activity")
            reasons.append("Growing network usage")
        
        # Sentiment reasons
        if sentiment_score >= 70:
            reasons.append("Positive market sentiment")
        elif sentiment_score >= 50:
            reasons.append("Neutral sentiment")
        
        # ATH-specific reasons
        ath_distance = coin_data.get("ath_distance_percent") or 0
        if ath_distance < -70:
            reasons.append("Significant discount from ATH")
            reasons.append("High upside potential")
        
        return reasons[:5]  # Limit to top 5 reasons
    
    def analyze_coin(self, coin_data: Dict[str, Any], price_history: Optional[List[float]] = None) -> Dict[str, Any]:
        """
        Main method to analyze a coin and generate AI prediction
        
        Returns comprehensive analysis with all scores and predictions
        """
        # 1. Technical Analysis
        if price_history and len(price_history) >= 14:
            tech_result = technical_analysis_service.get_technical_score(price_history)
            technical_score = tech_result["overall_score"]
        else:
            technical_score = 50.0  # Default if no price history
        
        # 2. Fundamental Analysis
        fundamental_score = self.calculate_fundamental_score(coin_data)
        
        # 3. On-chain Analysis
        onchain_score = self.calculate_onchain_score(coin_data)
        
        # 4. Sentiment Analysis
        sentiment_score = self.calculate_sentiment_score(coin_data)
        
        # 5. Historical Pattern Analysis
        historical_score = self.calculate_historical_score(coin_data)
        
        # Calculate weighted final AI score
        ai_recovery_score = (
            technical_score * self.weights["technical"] +
            fundamental_score * self.weights["fundamental"] +
            onchain_score * self.weights["onchain"] +
            sentiment_score * self.weights["sentiment"] +
            historical_score * self.weights["historical"]
        )
        
        # Get ATH distance
        ath_distance = coin_data.get("ath_distance_percent") or 0
        
        # Determine risk level
        market_cap_rank = coin_data.get("rank") or coin_data.get("market_cap_rank")
        risk_level = self.determine_risk_level(ai_recovery_score, market_cap_rank=market_cap_rank)
        
        # Calculate recovery probability
        recovery_probability = self.calculate_recovery_probability(
            ai_recovery_score, ath_distance, risk_level
        )
        
        # Estimate recovery time
        est_min, est_max = self.estimate_recovery_time(
            ai_recovery_score, ath_distance, risk_level
        )
        
        # Generate reasons
        reasons = self.generate_analysis_reasons(
            technical_score, fundamental_score, onchain_score, sentiment_score, coin_data
        )
        
        return {
            "ai_recovery_score": round(ai_recovery_score, 2),
            "recovery_probability": round(recovery_probability, 2),
            "estimated_recovery_months_min": est_min,
            "estimated_recovery_months_max": est_max,
            "risk_level": risk_level,
            "component_scores": {
                "technical": round(technical_score, 2),
                "fundamental": round(fundamental_score, 2),
                "onchain": round(onchain_score, 2),
                "sentiment": round(sentiment_score, 2),
                "historical": round(historical_score, 2),
            },
            "analysis_reasons": reasons,
            "model_version": self.model_version,
            "confidence_level": round(min(95, ai_recovery_score + 10), 2),  # Simple confidence metric
        }


# Singleton instance
ai_engine = AIRecoveryEngine()
