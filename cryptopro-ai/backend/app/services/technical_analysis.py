"""
Technical Analysis Service with 20+ professional indicators.
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class TechnicalIndicators:
    """Container for all technical indicators."""
    
    # Trend indicators
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None
    ema_12: Optional[float] = None
    ema_26: Optional[float] = None
    ema_20: Optional[float] = None
    ema_50: Optional[float] = None
    vwap: Optional[float] = None
    supertrend: Optional[float] = None
    
    # Momentum indicators
    rsi: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_histogram: Optional[float] = None
    stochastic_k: Optional[float] = None
    stochastic_d: Optional[float] = None
    cci: Optional[float] = None
    williams_r: Optional[float] = None
    roc: Optional[float] = None
    
    # Volatility indicators
    bollinger_upper: Optional[float] = None
    bollinger_middle: Optional[float] = None
    bollinger_lower: Optional[float] = None
    atr: Optional[float] = None
    keltner_upper: Optional[float] = None
    keltner_middle: Optional[float] = None
    keltner_lower: Optional[float] = None
    
    # Volume indicators
    obv: Optional[float] = None
    mfi: Optional[float] = None
    adl: Optional[float] = None
    
    # Trend strength
    adx: Optional[float] = None
    plus_di: Optional[float] = None
    minus_di: Optional[float] = None
    
    # Market structure
    trend: Optional[str] = None
    support_levels: List[float] = None
    resistance_levels: List[float] = None


class TechnicalAnalysisService:
    """
    Professional technical analysis service with 20+ indicators.
    """
    
    def __init__(self):
        self.min_periods_for_analysis = 60
    
    def calculate_all_indicators(
        self, 
        prices: pd.DataFrame
    ) -> TechnicalIndicators:
        """
        Calculate all technical indicators from price data.
        
        Args:
            prices: DataFrame with columns ['open', 'high', 'low', 'close', 'volume']
            
        Returns:
            TechnicalIndicators object with all calculated values
        """
        if len(prices) < self.min_periods_for_analysis:
            logger.warning(f"Insufficient data for analysis: {len(prices)} periods")
            return TechnicalIndicators()
        
        indicators = TechnicalIndicators()
        
        # Calculate all indicator groups
        self._calculate_trend_indicators(prices, indicators)
        self._calculate_momentum_indicators(prices, indicators)
        self._calculate_volatility_indicators(prices, indicators)
        self._calculate_volume_indicators(prices, indicators)
        self._calculate_adx(prices, indicators)
        self._detect_market_structure(prices, indicators)
        
        return indicators
    
    def _calculate_trend_indicators(self, prices: pd.DataFrame, ind: TechnicalIndicators):
        """Calculate trend-following indicators."""
        close = prices['close']
        high = prices['high']
        low = prices['low']
        volume = prices['volume']
        
        # Simple Moving Averages
        ind.sma_20 = float(close.rolling(window=20).mean().iloc[-1])
        ind.sma_50 = float(close.rolling(window=50).mean().iloc[-1])
        ind.sma_200 = float(close.rolling(window=200).mean().iloc[-1]) if len(close) >= 200 else None
        
        # Exponential Moving Averages
        ind.ema_12 = float(close.ewm(span=12, adjust=False).mean().iloc[-1])
        ind.ema_26 = float(close.ewm(span=26, adjust=False).mean().iloc[-1])
        ind.ema_20 = float(close.ewm(span=20, adjust=False).mean().iloc[-1])
        ind.ema_50 = float(close.ewm(span=50, adjust=False).mean().iloc[-1])
        
        # VWAP (Volume Weighted Average Price)
        typical_price = (high + low + close) / 3
        ind.vwap = float((typical_price * volume).cumsum() / volume.cumsum()).iloc[-1]
        
        # SuperTrend
        ind.supertrend = self._calculate_supertrend(high, low, close)
    
    def _calculate_momentum_indicators(self, prices: pd.DataFrame, ind: TechnicalIndicators):
        """Calculate momentum indicators."""
        close = prices['close']
        high = prices['high']
        low = prices['low']
        
        # RSI (Relative Strength Index)
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        ind.rsi = float(100 - (100 / (1 + rs))).iloc[-1]
        
        # MACD
        ema_12 = close.ewm(span=12, adjust=False).mean()
        ema_26 = close.ewm(span=26, adjust=False).mean()
        ind.macd = float((ema_12 - ema_26)).iloc[-1]
        ind.macd_signal = float(ind.macd if hasattr(ind, 'macd') else 0)
        ind.macd_signal = float(pd.Series(ind.macd if isinstance(ind.macd, (int, float)) else [ind.macd]).ewm(span=9).mean().iloc[-1]) if ind.macd else None
        ind.macd_histogram = (ind.macd - ind.macd_signal) if ind.macd and ind.macd_signal else None
        
        # Stochastic Oscillator
        lowest_low = low.rolling(window=14).min()
        highest_high = high.rolling(window=14).max()
        stoch_k = 100 * (close - lowest_low) / (highest_high - lowest_low)
        ind.stochastic_k = float(stoch_k).iloc[-1]
        ind.stochastic_d = float(stoch_k.rolling(window=3).mean()).iloc[-1]
        
        # CCI (Commodity Channel Index)
        tp = (high + low + close) / 3
        sma_tp = tp.rolling(window=20).mean()
        mad = tp.rolling(window=20).apply(lambda x: np.abs(x - x.mean()).mean())
        ind.cci = float((tp - sma_tp) / (0.015 * mad)).iloc[-1]
        
        # Williams %R
        highest_high_14 = high.rolling(window=14).max()
        lowest_low_14 = low.rolling(window=14).min()
        ind.williams_r = float(-100 * (highest_high_14 - close) / (highest_high_14 - lowest_low_14)).iloc[-1]
        
        # Rate of Change
        ind.roc = float(((close - close.shift(12)) / close.shift(12)) * 100).iloc[-1]
    
    def _calculate_volatility_indicators(self, prices: pd.DataFrame, ind: TechnicalIndicators):
        """Calculate volatility indicators."""
        close = prices['close']
        high = prices['high']
        low = prices['low']
        
        # Bollinger Bands
        ind.bollinger_middle = float(close.rolling(window=20).mean()).iloc[-1]
        std = float(close.rolling(window=20).std()).iloc[-1]
        ind.bollinger_upper = ind.bollinger_middle + 2 * std
        ind.bollinger_lower = ind.bollinger_middle - 2 * std
        
        # ATR (Average True Range)
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        ind.atr = float(tr.rolling(window=14).mean()).iloc[-1]
        
        # Keltner Channels
        ema_20 = close.ewm(span=20, adjust=False).mean()
        ind.keltner_middle = float(ema_20).iloc[-1]
        ind.keltner_upper = ind.keltner_middle + 2 * ind.atr if ind.atr else None
        ind.keltner_lower = ind.keltner_middle - 2 * ind.atr if ind.atr else None
    
    def _calculate_volume_indicators(self, prices: pd.DataFrame, ind: TechnicalIndicators):
        """Calculate volume-based indicators."""
        close = prices['close']
        high = prices['high']
        low = prices['low']
        volume = prices['volume']
        
        # OBV (On-Balance Volume)
        direction = np.sign(close.diff())
        direction[0] = 1
        ind.obv = float((direction * volume).cumsum()).iloc[-1]
        
        # MFI (Money Flow Index)
        typical_price = (high + low + close) / 3
        money_flow = typical_price * volume
        delta = typical_price.diff()
        positive_flow = money_flow.where(delta > 0, 0)
        negative_flow = money_flow.where(delta < 0, 0)
        positive_mf = positive_flow.rolling(window=14).sum()
        negative_mf = negative_flow.rolling(window=14).sum()
        mfi_ratio = positive_mf / negative_mf
        ind.mfi = float(100 - (100 / (1 + mfi_ratio))).iloc[-1]
        
        # ADL (Accumulation/Distribution Line)
        clv = ((close - low) - (high - close)) / (high - low)
        clv = clv.fillna(0)
        adl_series = (clv * volume).cumsum()
        ind.adl = float(adl_series).iloc[-1]
    
    def _calculate_adx(self, prices: pd.DataFrame, ind: TechnicalIndicators):
        """Calculate ADX (Average Directional Index)."""
        high = prices['high']
        low = prices['low']
        close = prices['close']
        
        plus_dm = high.diff()
        minus_dm = -low.diff()
        
        plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0)
        minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0)
        
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        atr = tr.rolling(window=14).mean()
        plus_di = 100 * (plus_dm.rolling(window=14).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=14).mean() / atr)
        
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        ind.adx = float(dx.rolling(window=14).mean()).iloc[-1]
        ind.plus_di = float(plus_di).iloc[-1]
        ind.minus_di = float(minus_di).iloc[-1]
    
    def _calculate_supertrend(self, high: pd.Series, low: pd.Series, close: pd.Series) -> Optional[float]:
        """Calculate SuperTrend indicator."""
        try:
            multiplier = 3.0
            period = 10
            
            tr1 = high - low
            tr2 = abs(high - close.shift(1))
            tr3 = abs(low - close.shift(1))
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(window=period).mean()
            
            hl2 = (high + low) / 2
            upper_band = hl2 + multiplier * atr
            lower_band = hl2 - multiplier * atr
            
            # Simplified supertrend value
            close_val = close.iloc[-1]
            lower_band_val = lower_band.iloc[-1]
            
            return float(lower_band_val) if close_val > lower_band_val else float(upper_band.iloc[-1])
        except Exception as e:
            logger.error(f"Error calculating SuperTrend: {e}")
            return None
    
    def _detect_market_structure(self, prices: pd.DataFrame, ind: TechnicalIndicators):
        """Detect market structure and key levels."""
        close = prices['close']
        high = prices['high']
        low = prices['low']
        
        # Detect trend
        if ind.sma_20 and ind.sma_50 and ind.sma_200:
            if ind.sma_20 > ind.sma_50 > ind.sma_200:
                ind.trend = "Strong Uptrend"
            elif ind.sma_20 < ind.sma_50 < ind.sma_200:
                ind.trend = "Strong Downtrend"
            elif ind.sma_20 > ind.sma_50:
                ind.trend = "Uptrend"
            elif ind.sma_20 < ind.sma_50:
                ind.trend = "Downtrend"
            else:
                ind.trend = "Sideways"
        else:
            ind.trend = "Unknown"
        
        # Find support and resistance levels (simplified)
        lookback = 50
        recent_highs = high.tail(lookback).nlargest(3)
        recent_lows = low.tail(lookback).nsmallest(3)
        
        ind.resistance_levels = [float(x) for x in recent_highs.values]
        ind.support_levels = [float(x) for x in recent_lows.values]
    
    def get_technical_score(self, indicators: TechnicalIndicators) -> Tuple[float, List[str]]:
        """
        Calculate overall technical score from indicators.
        
        Returns:
            Tuple of (score 0-100, list of signals)
        """
        score = 50.0  # Neutral starting point
        signals = []
        
        # RSI signals
        if indicators.rsi:
            if indicators.rsi < 30:
                score += 15
                signals.append("RSI Oversold - Bullish")
            elif indicators.rsi > 70:
                score -= 15
                signals.append("RSI Overbought - Bearish")
            elif indicators.rsi < 40:
                score += 5
                signals.append("RSI Low - Slightly Bullish")
            elif indicators.rsi > 60:
                score -= 5
                signals.append("RSI High - Slightly Bearish")
        
        # MACD signals
        if indicators.macd and indicators.macd_signal:
            if indicators.macd > indicators.macd_signal:
                score += 10
                signals.append("MACD Bullish Crossover")
            else:
                score -= 10
                signals.append("MACD Bearish Crossover")
        
        # Moving average signals
        if indicators.sma_20 and indicators.sma_50:
            if indicators.sma_20 > indicators.sma_50:
                score += 10
                signals.append("Price Above SMA20/50 - Bullish")
            else:
                score -= 10
                signals.append("Price Below SMA20/50 - Bearish")
        
        # Trend signals
        if indicators.trend == "Strong Uptrend":
            score += 15
            signals.append("Strong Uptrend Detected")
        elif indicators.trend == "Strong Downtrend":
            score -= 15
            signals.append("Strong Downtrend Detected")
        
        # Bollinger Band signals
        current_price = indicators.bollinger_middle  # Approximation
        if indicators.bollinger_lower and current_price:
            if current_price < indicators.bollinger_lower * 1.02:
                score += 10
                signals.append("Price Near Lower Bollinger Band - Potential Reversal")
        
        # ADX signals
        if indicators.adx:
            if indicators.adx > 25:
                signals.append(f"Strong Trend (ADX: {indicators.adx:.1f})")
            else:
                signals.append(f"Weak Trend (ADX: {indicators.adx:.1f})")
        
        # Clamp score between 0 and 100
        score = max(0, min(100, score))
        
        return score, signals
