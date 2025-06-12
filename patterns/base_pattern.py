from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class CandleData:
    """K线数据结构"""
    open: float      # 开盘价
    high: float      # 最高价
    low: float       # 最低价
    close: float     # 收盘价
    volume: float    # 成交量
    datetime: datetime  # 时间戳

@dataclass
class PatternResult:
    """形态识别结果数据结构"""
    pattern_name: str    # 形态名称
    is_detected: bool    # 是否检测到形态
    datetime: datetime   # 时间戳
    additional_info: Optional[dict] = None  # 额外信息（可选）

class BasePatternDetector:
    """形态检测器基类"""
    def __init__(self, trend_periods: int = 5,
                 min_consecutive_lower_lows: int = 3):
        """
        初始化形态检测器基类
        
        参数:
            trend_periods: 趋势判断周期数
            min_consecutive_lower_lows: 最小连续低点数量
        """
        self.trend_periods = trend_periods
        self.min_consecutive_lower_lows = min_consecutive_lower_lows
        self.previous_candles: List[CandleData] = []

    def is_downtrend(self) -> bool:
        """
        检查是否处于下跌趋势，且至少有一根K线下跌幅度超过0.5%
        
        返回:
            bool: 是否处于下跌趋势且满足下跌幅度要求
        """
        if len(self.previous_candles) < self.min_consecutive_lower_lows:
            return False

        # 检查最近三根K线是否连续下跌且为阴线
        last_candle = self.previous_candles[-1]
        second_last_candle = self.previous_candles[-2]
        third_last_candle = self.previous_candles[-3]
        
        # 计算每根K线的下跌幅度
        drop1 = (last_candle['open'] -  last_candle['close']) / last_candle['open']
        drop2 = (second_last_candle['open'] - second_last_candle['close']) / second_last_candle['open']
        drop3 = (third_last_candle['open'] - third_last_candle['close']) / third_last_candle['open']
        
        # 判断是否连续下跌（收盘价低于前一根K线）且为阴线（收盘价低于开盘价）
        # 且至少有一根K线下跌幅度超过0.5%
        return (last_candle['close'] < second_last_candle['close'] and 
                second_last_candle['close'] < third_last_candle['close'] and
                last_candle['close'] < last_candle['open'] and
                second_last_candle['close'] < second_last_candle['open'] and
                third_last_candle['close'] < third_last_candle['open'] and
                (drop1 >= 0.005 or drop2 >= 0.005 or drop3 >= 0.005))  # 0.005 = 0.5%

    def update_candles(self, candle: CandleData):
        """
        更新K线历史数据
        
        参数:
            candle: 新的K线数据
        """
        self.previous_candles.append({
            'close': candle.close[0],
            'open': candle.open[0],
        })
        # 只保留最近的trend_periods + 1根K线
        if len(self.previous_candles) > self.trend_periods + 1:
            self.previous_candles.pop(0) 