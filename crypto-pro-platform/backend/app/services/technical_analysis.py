"""
Technical Analysis Service
Provides comprehensive technical indicator calculations and analysis
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class TechnicalIndicators:
    """Container for all calculated technical indicators"""
    rsi: float
    macd: float
    macd_signal: float
    macd_histogram: float
    ema_12: float
    ema_26: float
    ema_50: float
    sma_50: float
    sma_200: float
    bollinger_upper: float
    bollinger_middle: float
    bollinger_lower: float
    atr: float
    stochastic_k: float
    stochastic_d: float
    williams_r: float
    cci: float
    adx: float
    plus_di: float
    minus_di: float
    obv: float
    volume_sma: float
    vwap: float
    pivot_point: float
    resistance_1: float
    resistance_2: float
    support_1: float
    support_2: float


class TechnicalAnalysisService:
    """
    Professional-grade technical analysis service.
    
    Implements industry-standard technical indicators used by
    professional traders and analysts.
    """
    
    def __init__(self):
        self.indicators = {}
    
    def calculate_all_indicators(
        self,
        prices: List[float],
        highs: List[float],
        lows: List[float],
        volumes: List[float],
        timestamps: Optional[List] = None
    ) -> TechnicalIndicators:
        """
        Calculate all technical indicators from price data.
        
        Args:
            prices: List of closing prices
            highs: List of high prices
            lows: List of low prices
            volumes: List of volumes
            timestamps: Optional list of timestamps
            
        Returns:
            TechnicalIndicators dataclass with all calculated values
        """
        # Convert to pandas Series for easier calculation
        close = pd.Series(prices)
        high = pd.Series(highs)
        low = pd.Series(lows)
        volume = pd.Series(volumes)
        
        # Calculate indicators
        rsi = self._calculate_rsi(close)
        macd, macd_signal, macd_hist = self._calculate_macd(close)
        ema_12 = self._calculate_ema(close, 12)
        ema_26 = self._calculate_ema(close, 26)
        ema_50 = self._calculate_ema(close, 50)
        sma_50 = self._calculate_sma(close, 50)
        sma_200 = self._calculate_sma(close, 200) if len(close) >= 200 else None
        
        bb_upper, bb_middle, bb_lower = self._calculate_bollinger_bands(close)
        atr = self._calculate_atr(high, low, close)
        
        stoch_k, stoch_d = self._calculate_stochastic(high, low, close)
        williams_r = self._calculate_williams_r(high, low, close)
        cci = self._calculate_cci(high, low, close)
        
        adx, plus_di, minus_di = self._calculate_adx(high, low, close)
        
        obv = self._calculate_obv(close, volume)
        volume_sma = self._calculate_sma(volume, 20)
        vwap = self._calculate_vwap(high, low, close, volume)
        
        pivot, r1, r2, s1, s2 = self._calculate_pivot_points(
            high.iloc[-1], low.iloc[-1], close.iloc[-1]
        )
        
        return TechnicalIndicators(
            rsi=rsi,
            macd=macd,
            macd_signal=macd_signal,
            macd_histogram=macd_hist,
            ema_12=ema_12,
            ema_26=ema_26,
            ema_50=ema_50,
            sma_50=sma_50,
            sma_200=sma_200,
            bollinger_upper=bb_upper,
            bollinger_middle=bb_middle,
            bollinger_lower=bb_lower,
            atr=atr,
            stochastic_k=stoch_k,
            stochastic_d=stoch_d,
            williams_r=williams_r,
            cci=cci,
            adx=adx,
            plus_di=plus_di,
            minus_di=minus_di,
            obv=obv,
            volume_sma=volume_sma,
            vwap=vwap,
            pivot_point=pivot,
            resistance_1=r1,
            resistance_2=r2,
            support_1=s1,
            support_2=s2,
        )
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """Calculate Relative Strength Index (RSI)"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return round(rsi.iloc[-1], 2) if not pd.isna(rsi.iloc[-1]) else 50.0
    
    def _calculate_macd(
        self,
        prices: pd.Series,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9
    ) -> Tuple[float, float, float]:
        """Calculate MACD, Signal Line, and Histogram"""
        ema_fast = self._calculate_ema(prices, fast)
        ema_slow = self._calculate_ema(prices, slow)
        
        macd_line = ema_fast - ema_slow
        signal_line = self._calculate_ema(pd.Series(macd_line), signal)
        histogram = macd_line - signal_line
        
        return (
            round(macd_line.iloc[-1], 4),
            round(signal_line.iloc[-1], 4),
            round(histogram.iloc[-1], 4)
        )
    
    def _calculate_ema(self, prices: pd.Series, period: int) -> float:
        """Calculate Exponential Moving Average"""
        ema = prices.ewm(span=period, adjust=False).mean()
        return round(ema.iloc[-1], 4) if not pd.isna(ema.iloc[-1]) else prices.iloc[-1]
    
    def _calculate_sma(self, prices: pd.Series, period: int) -> Optional[float]:
        """Calculate Simple Moving Average"""
        if len(prices) < period:
            return None
        sma = prices.rolling(window=period).mean()
        return round(sma.iloc[-1], 4) if not pd.isna(sma.iloc[-1]) else None
    
    def _calculate_bollinger_bands(
        self,
        prices: pd.Series,
        period: int = 20,
        std_dev: float = 2.0
    ) -> Tuple[float, float, float]:
        """Calculate Bollinger Bands"""
        middle = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        
        upper = middle + (std_dev * std)
        lower = middle - (std_dev * std)
        
        return (
            round(upper.iloc[-1], 4),
            round(middle.iloc[-1], 4),
            round(lower.iloc[-1], 4)
        )
    
    def _calculate_atr(
        self,
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period: int = 14
    ) -> float:
        """Calculate Average True Range (ATR)"""
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        return round(atr.iloc[-1], 4) if not pd.isna(atr.iloc[-1]) else 0.0
    
    def _calculate_stochastic(
        self,
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        k_period: int = 14,
        d_period: int = 3
    ) -> Tuple[float, float]:
        """Calculate Stochastic Oscillator"""
        lowest_low = low.rolling(window=k_period).min()
        highest_high = high.rolling(window=k_period).max()
        
        k = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d = k.rolling(window=d_period).mean()
        
        return (
            round(k.iloc[-1], 2) if not pd.isna(k.iloc[-1]) else 50.0,
            round(d.iloc[-1], 2) if not pd.isna(d.iloc[-1]) else 50.0
        )
    
    def _calculate_williams_r(
        self,
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period: int = 14
    ) -> float:
        """Calculate Williams %R"""
        highest_high = high.rolling(window=period).max()
        lowest_low = low.rolling(window=period).min()
        
        wr = -100 * ((highest_high - close) / (highest_high - lowest_low))
        
        return round(wr.iloc[-1], 2) if not pd.isna(wr.iloc[-1]) else -50.0
    
    def _calculate_cci(
        self,
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period: int = 20
    ) -> float:
        """Calculate Commodity Channel Index (CCI)"""
        tp = (high + low + close) / 3  # Typical Price
        sma_tp = tp.rolling(window=period).mean()
        mean_dev = tp.rolling(window=period).apply(lambda x: np.abs(x - x.mean()).mean())
        
        cci = (tp - sma_tp) / (0.015 * mean_dev)
        
        return round(cci.iloc[-1], 2) if not pd.isna(cci.iloc[-1]) else 0.0
    
    def _calculate_adx(
        self,
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period: int = 14
    ) -> Tuple[float, float, float]:
        """Calculate Average Directional Index (ADX)"""
        plus_dm = high.diff()
        minus_dm = -low.diff()
        
        plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0)
        minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0)
        
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        atr = tr.rolling(window=period).mean()
        
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
        
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()
        
        return (
            round(adx.iloc[-1], 2) if not pd.isna(adx.iloc[-1]) else 25.0,
            round(plus_di.iloc[-1], 2) if not pd.isna(plus_di.iloc[-1]) else 25.0,
            round(minus_di.iloc[-1], 2) if not pd.isna(minus_di.iloc[-1]) else 25.0
        )
    
    def _calculate_obv(self, close: pd.Series, volume: pd.Series) -> float:
        """Calculate On-Balance Volume (OBV)"""
        direction = np.sign(close.diff())
        obv = (volume * direction).cumsum()
        
        return round(obv.iloc[-1], 0) if not pd.isna(obv.iloc[-1]) else 0.0
    
    def _calculate_vwap(
        self,
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        volume: pd.Series
    ) -> float:
        """Calculate Volume Weighted Average Price (VWAP)"""
        tp = (high + low + close) / 3
        vwap = (tp * volume).cumsum() / volume.cumsum()
        
        return round(vwap.iloc[-1], 4) if not pd.isna(vwap.iloc[-1]) else close.iloc[-1]
    
    def _calculate_pivot_points(
        self,
        high: float,
        low: float,
        close: float
    ) -> Tuple[float, float, float, float, float]:
        """Calculate Pivot Points and Support/Resistance levels"""
        pivot = (high + low + close) / 3
        
        r1 = (2 * pivot) - low
        r2 = pivot + (high - low)
        s1 = (2 * pivot) - high
        s2 = pivot - (high - low)
        
        return (
            round(pivot, 4),
            round(r1, 4),
            round(r2, 4),
            round(s1, 4),
            round(s2, 4)
        )
    
    def analyze_trend(self, indicators: TechnicalIndicators) -> Dict[str, any]:
        """
        Analyze overall trend based on technical indicators.
        
        Returns:
            Dictionary with trend analysis results
        """
        trend_signals = {
            "bullish": 0,
            "bearish": 0,
            "neutral": 0,
            "signals": []
        }
        
        # RSI Analysis
        if indicators.rsi < 30:
            trend_signals["bullish"] += 2
            trend_signals["signals"].append("RSI Oversold")
        elif indicators.rsi > 70:
            trend_signals["bearish"] += 2
            trend_signals["signals"].append("RSI Overbought")
        
        # MACD Analysis
        if indicators.macd > indicators.macd_signal:
            trend_signals["bullish"] += 2
            trend_signals["signals"].append("MACD Bullish Crossover")
        else:
            trend_signals["bearish"] += 2
            trend_signals["signals"].append("MACD Bearish Crossover")
        
        # EMA Analysis
        if indicators.ema_12 > indicators.ema_26:
            trend_signals["bullish"] += 1
            trend_signals["signals"].append("EMA12 > EMA26")
        else:
            trend_signals["bearish"] += 1
        
        # Bollinger Bands Analysis
        current_price = indicators.bollinger_middle  # Approximation
        if current_price < indicators.bollinger_lower:
            trend_signals["bullish"] += 2
            trend_signals["signals"].append("Price Below Lower BB")
        elif current_price > indicators.bollinger_upper:
            trend_signals["bearish"] += 2
            trend_signals["signals"].append("Price Above Upper BB")
        
        # ADX Trend Strength
        if indicators.adx > 25:
            trend_signals["signals"].append(f"Strong Trend (ADX: {indicators.adx})")
        else:
            trend_signals["signals"].append(f"Weak Trend (ADX: {indicators.adx})")
        
        # Determine overall trend
        if trend_signals["bullish"] > trend_signals["bearish"]:
            trend_signals["overall"] = "BULLISH"
            trend_signals["strength"] = min(100, (trend_signals["bullish"] / 
                (trend_signals["bullish"] + trend_signals["bearish"])) * 100)
        elif trend_signals["bearish"] > trend_signals["bullish"]:
            trend_signals["overall"] = "BEARISH"
            trend_signals["strength"] = min(100, (trend_signals["bearish"] / 
                (trend_signals["bullish"] + trend_signals["bearish"])) * 100)
        else:
            trend_signals["overall"] = "NEUTRAL"
            trend_signals["strength"] = 50
        
        return trend_signals
    
    def calculate_technical_score(self, indicators: TechnicalIndicators) -> float:
        """
        Calculate overall technical score (0-100).
        
        Higher score indicates more bullish technical conditions.
        """
        score = 50.0  # Start neutral
        
        # RSI Component (15 points)
        if 30 <= indicators.rsi <= 70:
            score += (50 - indicators.rsi) / 10  # Neutral RSI
        elif indicators.rsi < 30:
            score += 15  # Oversold - bullish
        else:
            score -= 15  # Overbought - bearish
        
        # MACD Component (15 points)
        if indicators.macd > indicators.macd_signal:
            score += 15
        else:
            score -= 15
        
        # Price vs EMA Component (10 points)
        # Assuming current price is close to the latest value
        if indicators.ema_12 > indicators.ema_50:
            score += 10
        else:
            score -= 10
        
        # Bollinger Bands Component (10 points)
        if indicators.bollinger_middle > indicators.bollinger_lower:
            score += 5
        
        # Trend Strength Component (10 points)
        if indicators.adx > 25:
            if indicators.plus_di > indicators.minus_di:
                score += 10
            else:
                score -= 10
        
        # Normalize to 0-100
        return max(0, min(100, score))


# Singleton instance
technical_analysis_service = TechnicalAnalysisService()
