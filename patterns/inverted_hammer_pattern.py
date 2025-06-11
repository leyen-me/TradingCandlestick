from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class CandleData:
    open: float
    high: float
    low: float
    close: float
    volume: float
    timestamp: datetime

@dataclass
class PatternResult:
    pattern_name: str
    is_detected: bool
    confidence: float
    timestamp: datetime
    symbol: str
    additional_info: Optional[dict] = None

class InvertedHammerPatternDetector:
    def __init__(self, body_ratio_threshold: float = 0.3, 
                 upper_shadow_ratio_threshold: float = 2.0,
                 trend_periods: int = 5,
                 min_trend_strength: float = 0.002,
                 max_reversal_candles: int = 3):
        """
        Initialize the inverted hammer pattern detector
        
        Args:
            body_ratio_threshold: Maximum ratio of body to total candle height (default: 0.3)
            upper_shadow_ratio_threshold: Minimum ratio of upper shadow to body (default: 2.0)
            trend_periods: Number of periods to analyze for trend (default: 5)
            min_trend_strength: Minimum price change to consider as significant trend (default: 0.002 or 0.2%)
            max_reversal_candles: Maximum number of reversal candles to consider (default: 3)
        """
        self.body_ratio_threshold = body_ratio_threshold
        self.upper_shadow_ratio_threshold = upper_shadow_ratio_threshold
        self.trend_periods = trend_periods
        self.min_trend_strength = min_trend_strength
        self.max_reversal_candles = max_reversal_candles
        self.previous_candles: List[CandleData] = []

    def is_downtrend(self) -> bool:
        """
        Check if the current market is in a downtrend
        
        Returns:
            bool: True if in downtrend, False otherwise
        """
        if len(self.previous_candles) < self.trend_periods:
            return False

        # Calculate overall trend strength
        start_price = self.previous_candles[-self.trend_periods].close
        end_price = self.previous_candles[-1].close
        trend_strength = (start_price - end_price) / start_price

        # Check for consecutive bearish candles
        consecutive_bearish = 0
        consecutive_bullish = 0
        max_consecutive_bullish = 0

        for i in range(-self.trend_periods, 0):
            candle = self.previous_candles[i]
            if candle.close < candle.open:  # Bearish candle
                consecutive_bearish += 1
                consecutive_bullish = 0
            else:  # Bullish candle
                consecutive_bullish += 1
                max_consecutive_bullish = max(max_consecutive_bullish, consecutive_bullish)
                consecutive_bearish = 0

        return (trend_strength >= self.min_trend_strength and 
                consecutive_bearish >= 3 and 
                max_consecutive_bullish <= self.max_reversal_candles)

    def update_candles(self, candle: CandleData):
        """
        Update the list of previous candles
        
        Args:
            candle: New candle data
        """
        self.previous_candles.append(candle)
        # Keep only the last trend_periods + 1 candles
        if len(self.previous_candles) > self.trend_periods + 1:
            self.previous_candles.pop(0)

    def detect(self, open_price: float, high: float, low: float, close: float, 
              volume: float, symbol: str, timestamp: datetime) -> PatternResult:
        """
        Detect if the current candle forms an inverted hammer pattern
        
        Args:
            open_price: Opening price
            high: Highest price
            low: Lowest price
            close: Closing price
            volume: Trading volume
            symbol: Stock symbol
            timestamp: Candle timestamp
            
        Returns:
            PatternResult object containing detection results
        """
        # Create new candle data
        current_candle = CandleData(
            open=open_price,
            high=high,
            low=low,
            close=close,
            volume=volume,
            timestamp=timestamp
        )
        
        # Update candle history
        self.update_candles(current_candle)
        
        # Calculate candle components
        body = abs(close - open_price)
        total_height = high - low
        upper_shadow = high - max(open_price, close)
        lower_shadow = min(open_price, close) - low
        
        # Check if it's a bullish candle (close > open)
        is_bullish = close > open_price
        
        # Calculate ratios
        body_ratio = body / total_height if total_height > 0 else 0
        upper_shadow_ratio = upper_shadow / body if body > 0 else 0
        
        # Check for downtrend
        in_downtrend = self.is_downtrend()
        
        # Pattern detection conditions
        is_inverted_hammer = (
            body_ratio <= self.body_ratio_threshold and  # Small body
            upper_shadow_ratio >= self.upper_shadow_ratio_threshold and  # Long upper shadow
            lower_shadow <= body * 0.1 and  # Very small or no lower shadow
            is_bullish and  # Bullish candle
            in_downtrend  # Must be in downtrend
        )
        
        # Calculate confidence score (0-1)
        confidence = 0.0
        if is_inverted_hammer:
            # Base confidence on pattern characteristics
            pattern_confidence = min(1.0, (self.upper_shadow_ratio_threshold / upper_shadow_ratio) * 
                                  (body_ratio / self.body_ratio_threshold))
            
            # Adjust confidence based on trend strength
            trend_strength = min(1.0, abs(self.previous_candles[-self.trend_periods].close - 
                                        self.previous_candles[-1].close) / 
                                        self.previous_candles[-self.trend_periods].close)
            
            confidence = (pattern_confidence + trend_strength) / 2
        
        return PatternResult(
            pattern_name="Inverted Hammer",
            is_detected=is_inverted_hammer,
            confidence=confidence,
            timestamp=timestamp,
            symbol=symbol,
            additional_info={
                "body_ratio": body_ratio,
                "upper_shadow_ratio": upper_shadow_ratio,
                "lower_shadow": lower_shadow,
                "is_bullish": is_bullish,
                "in_downtrend": in_downtrend,
                "trend_strength": abs(self.previous_candles[-self.trend_periods].close - 
                                    self.previous_candles[-1].close) / 
                                    self.previous_candles[-self.trend_periods].close if in_downtrend else 0
            }
        ) 