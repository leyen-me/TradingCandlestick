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

class HammerPatternDetector:
    def __init__(self, body_ratio_threshold: float = 0.3, 
                 shadow_ratio_threshold: float = 2.0,
                 trend_periods: int = 5,
                 min_trend_strength: float = 0.005,
                 max_reversal_candles: int = 3):
        """
        Initialize the hammer pattern detector
        
        Args:
            body_ratio_threshold: Maximum ratio of body to total candle height (default: 0.3)
            shadow_ratio_threshold: Minimum ratio of lower shadow to body (default: 2.0)
            trend_periods: Number of periods to analyze for trend (default: 5)
            min_trend_strength: Minimum price change to consider as significant trend (default: 0.005 or 0.5%)
            max_reversal_candles: Maximum number of reversal candles to consider (default: 3)
        """
        self.body_ratio_threshold = body_ratio_threshold
        self.shadow_ratio_threshold = shadow_ratio_threshold
        self.trend_periods = trend_periods
        self.min_trend_strength = min_trend_strength
        self.max_reversal_candles = max_reversal_candles
        self.previous_candles: List[CandleData] = []

    def is_downtrend(self) -> bool:
        """
        Check if the current market is in a downtrend by verifying consecutive bearish candles
        and considering the overall trend strength
        
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

        # Consider it a downtrend if:
        # 1. Overall trend is down (price decreased by min_trend_strength)
        # 2. Has at least 3 consecutive bearish candles
        # 3. Any bullish candles don't exceed max_reversal_candles
        return (trend_strength >= self.min_trend_strength and 
                consecutive_bearish >= 3 and 
                max_consecutive_bullish <= self.max_reversal_candles)

    def is_false_breakout(self) -> bool:
        """
        Check if the current pattern might be a false breakout
        
        Returns:
            bool: True if likely a false breakout, False otherwise
        """
        if len(self.previous_candles) < 3:
            return False

        # Check last 3 candles
        last_3_candles = self.previous_candles[-3:]
        
        # Count bullish candles
        bullish_count = sum(1 for c in last_3_candles if c.close > c.open)
        
        # Calculate price movement
        start_price = last_3_candles[0].close
        end_price = last_3_candles[-1].close
        price_change = (end_price - start_price) / start_price
        
        # Consider it a false breakout if:
        # 1. Has 1-3 bullish candles
        # 2. Price change is relatively small (less than min_trend_strength)
        # 3. Last candle is bearish
        return (1 <= bullish_count <= self.max_reversal_candles and
                abs(price_change) < self.min_trend_strength and
                last_3_candles[-1].close < last_3_candles[-1].open)

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
        Detect if the current candle forms a hammer pattern
        
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
        shadow_ratio = lower_shadow / body if body > 0 else 0
        
        # Check for downtrend and false breakout
        in_downtrend = self.is_downtrend()
        is_false_breakout = self.is_false_breakout()
        
        # Pattern detection conditions
        is_hammer = (
            body_ratio <= self.body_ratio_threshold and  # Small body
            shadow_ratio >= self.shadow_ratio_threshold and  # Long lower shadow
            upper_shadow <= body * 0.1 and  # Very small or no upper shadow
            is_bullish and  # Bullish candle
            in_downtrend and  # Must be in downtrend
            not is_false_breakout  # Must not be a false breakout
        )
        
        # Calculate confidence score (0-1)
        confidence = 0.0
        if is_hammer:
            # Base confidence on pattern characteristics
            pattern_confidence = min(1.0, (self.shadow_ratio_threshold / shadow_ratio) * 
                                  (body_ratio / self.body_ratio_threshold))
            
            # Adjust confidence based on trend strength
            trend_strength = min(1.0, abs(self.previous_candles[-self.trend_periods].close - 
                                        self.previous_candles[-1].close) / 
                                        self.previous_candles[-self.trend_periods].close)
            
            confidence = (pattern_confidence + trend_strength) / 2
        
        return PatternResult(
            pattern_name="Hammer",
            is_detected=is_hammer,
            confidence=confidence,
            timestamp=timestamp,
            symbol=symbol,
            additional_info={
                "body_ratio": body_ratio,
                "shadow_ratio": shadow_ratio,
                "upper_shadow": upper_shadow,
                "lower_shadow": lower_shadow,
                "is_bullish": is_bullish,
                "in_downtrend": in_downtrend,
                "is_false_breakout": is_false_breakout,
                "trend_strength": abs(self.previous_candles[-self.trend_periods].close - 
                                    self.previous_candles[-1].close) / 
                                    self.previous_candles[-self.trend_periods].close if in_downtrend else 0
            }
        ) 