"""
Technical Analysis Service - Calculate technical indicators
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any
from loguru import logger


class TechnicalAnalysisService:
    """Service for calculating technical indicators"""
    
    def __init__(self):
        pass
    
    def calculate_rsi(self, prices: List[float], period: int = 14) -> Optional[float]:
        """Calculate RSI (Relative Strength Index)"""
        if len(prices) < period + 1:
            return None
        
        try:
            deltas = np.diff(prices)
            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)
            
            avg_gain = np.mean(gains[-period:])
            avg_loss = np.mean(losses[-period:])
            
            if avg_loss == 0:
                return 100.0
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            return round(rsi, 2)
        except Exception as e:
            logger.error(f"Error calculating RSI: {e}")
            return None
    
    def calculate_macd(
        self, 
        prices: List[float], 
        fast_period: int = 12, 
        slow_period: int = 26, 
        signal_period: int = 9
    ) -> Optional[Dict[str, float]]:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        if len(prices) < slow_period + signal_period:
            return None
        
        try:
            series = pd.Series(prices)
            
            ema_fast = series.ewm(span=fast_period, adjust=False).mean()
            ema_slow = series.ewm(span=slow_period, adjust=False).mean()
            
            macd_line = ema_fast - ema_slow
            signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
            histogram = macd_line - signal_line
            
            return {
                "macd": round(macd_line.iloc[-1], 4),
                "signal": round(signal_line.iloc[-1], 4),
                "histogram": round(histogram.iloc[-1], 4),
            }
        except Exception as e:
            logger.error(f"Error calculating MACD: {e}")
            return None
    
    def calculate_ema(self, prices: List[float], period: int) -> Optional[float]:
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return None
        
        try:
            series = pd.Series(prices)
            ema = series.ewm(span=period, adjust=False).mean()
            return round(ema.iloc[-1], 4)
        except Exception as e:
            logger.error(f"Error calculating EMA: {e}")
            return None
    
    def calculate_sma(self, prices: List[float], period: int) -> Optional[float]:
        """Calculate Simple Moving Average"""
        if len(prices) < period:
            return None
        
        try:
            sma = np.mean(prices[-period:])
            return round(sma, 4)
        except Exception as e:
            logger.error(f"Error calculating SMA: {e}")
            return None
    
    def calculate_bollinger_bands(
        self, 
        prices: List[float], 
        period: int = 20, 
        std_dev: float = 2.0
    ) -> Optional[Dict[str, float]]:
        """Calculate Bollinger Bands"""
        if len(prices) < period:
            return None
        
        try:
            series = pd.Series(prices)
            sma = series.rolling(window=period).mean()
            std = series.rolling(window=period).std()
            
            upper_band = sma + (std * std_dev)
            lower_band = sma - (std * std_dev)
            
            return {
                "upper": round(upper_band.iloc[-1], 4),
                "middle": round(sma.iloc[-1], 4),
                "lower": round(lower_band.iloc[-1], 4),
            }
        except Exception as e:
            logger.error(f"Error calculating Bollinger Bands: {e}")
            return None
    
    def calculate_atr(
        self, 
        high: List[float], 
        low: List[float], 
        close: List[float], 
        period: int = 14
    ) -> Optional[float]:
        """Calculate Average True Range (ATR)"""
        if len(high) < period or len(low) < period or len(close) < period:
            return None
        
        try:
            high = np.array(high)
            low = np.array(low)
            close = np.array(close)
            
            prev_close = np.roll(close, 1)
            prev_close[0] = close[0]
            
            tr1 = high - low
            tr2 = np.abs(high - prev_close)
            tr3 = np.abs(low - prev_close)
            
            true_range = np.maximum(np.maximum(tr1, tr2), tr3)
            atr = np.mean(true_range[-period:])
            
            return round(atr, 4)
        except Exception as e:
            logger.error(f"Error calculating ATR: {e}")
            return None
    
    def calculate_vwap(
        self, 
        high: List[float], 
        low: List[float], 
        close: List[float], 
        volume: List[float]
    ) -> Optional[float]:
        """Calculate Volume Weighted Average Price (VWAP)"""
        if not all([high, low, close, volume]):
            return None
        
        try:
            typical_price = [(h + l + c) / 3 for h, l, c in zip(high, low, close)]
            
            tpv = [tp * v for tp, v in zip(typical_price, volume)]
            cumulative_tpv = sum(tpv)
            cumulative_volume = sum(volume)
            
            if cumulative_volume == 0:
                return None
            
            vwap = cumulative_tpv / cumulative_volume
            return round(vwap, 4)
        except Exception as e:
            logger.error(f"Error calculating VWAP: {e}")
            return None
    
    def get_technical_score(self, prices: List[float], **kwargs) -> Dict[str, Any]:
        """
        Calculate overall technical analysis score (0-100)
        
        Returns comprehensive technical analysis with individual indicators and overall score
        """
        score_components = []
        signals = {"bullish": [], "bearish": [], "neutral": []}
        
        # RSI Analysis
        rsi = self.calculate_rsi(prices)
        if rsi is not None:
            if rsi < 30:
                score_components.append(85)
                signals["bullish"].append("RSI oversold")
            elif rsi > 70:
                score_components.append(20)
                signals["bearish"].append("RSI overbought")
            else:
                score_components.append(50)
                signals["neutral"].append(f"RSI neutral at {rsi}")
        
        # MACD Analysis
        macd_data = self.calculate_macd(prices)
        if macd_data:
            if macd_data["histogram"] > 0:
                score_components.append(70)
                signals["bullish"].append("MACD bullish crossover")
            else:
                score_components.append(30)
                signals["bearish"].append("MACD bearish")
        
        # EMA Trend
        if len(prices) >= 50:
            ema_20 = self.calculate_ema(prices, 20)
            ema_50 = self.calculate_ema(prices, 50)
            current_price = prices[-1]
            
            if ema_20 and ema_50:
                if current_price > ema_20 > ema_50:
                    score_components.append(80)
                    signals["bullish"].append("Price above EMAs (uptrend)")
                elif current_price < ema_20 < ema_50:
                    score_components.append(25)
                    signals["bearish"].append("Price below EMAs (downtrend)")
                else:
                    score_components.append(50)
                    signals["neutral"].append("Mixed EMA signals")
        
        # Calculate overall score
        if score_components:
            overall_score = sum(score_components) / len(score_components)
        else:
            overall_score = 50
        
        return {
            "overall_score": round(overall_score, 2),
            "rsi": rsi,
            "macd": macd_data,
            "signals": signals,
        }


# Singleton instance
technical_analysis_service = TechnicalAnalysisService()
