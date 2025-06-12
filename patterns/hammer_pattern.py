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

class HammerPatternDetector:
    """锤子线形态检测器"""
    def __init__(self, min_lower_shadow: float = 1.5, 
                 max_upper_shadow: float = 0.8,
                 trend_periods: int = 5,
                 min_consecutive_lower_lows: int = 3):
        """
        初始化锤子线检测器
        
        参数:
            min_lower_shadow: 下影线最小长度（相对于实体）
            max_upper_shadow: 上影线最大长度（相对于实体）
            trend_periods: 趋势判断周期数
            min_trend_strength: 最小趋势强度（价格变化百分比）
            min_consecutive_lower_lows: 最小连续低点数量
        """
        self.min_lower_shadow = min_lower_shadow
        self.max_upper_shadow = max_upper_shadow
        self.trend_periods = trend_periods
        self.min_consecutive_lower_lows = min_consecutive_lower_lows
        self.previous_candles: List[CandleData] = []

    def is_downtrend(self) -> bool:
        """
        检查锤子线之前的两根K线是否连续下跌
        
        返回:
            bool: 是否连续下跌
        """
        if len(self.previous_candles) < self.min_consecutive_lower_lows:
            return False

        # 检查最近三根K线是否连续下跌
        last_candle = self.previous_candles[-1]
        second_last_candle = self.previous_candles[-2]
        third_last_candle = self.previous_candles[-3]
        
        # 判断是否连续下跌（收盘价低于前一根K线）
        return last_candle['close'] < second_last_candle['close'] and second_last_candle['close'] < third_last_candle['close']

    def update_candles(self, candle: CandleData):
        """
        更新K线历史数据
        
        参数:
            candle: 新的K线数据
        """
        self.previous_candles.append({
            'close': candle.close[0],
        })
        # 只保留最近的trend_periods + 1根K线
        if len(self.previous_candles) > self.trend_periods + 1:
            self.previous_candles.pop(0)

    def detect(self, data: CandleData) -> PatternResult:
        """
        检测当前K线是否形成锤子线形态
        
        参数:
            data: CandleData对象，包含K线数据
            
        返回:
            PatternResult对象，包含检测结果
        """
         # 检查是否处于下跌趋势
        in_downtrend = self.is_downtrend()
        
        # 更新K线历史
        self.update_candles(data)
        
        # 计算K线各组成部分
        body = abs(data.close - data.open)  # 实体长度
        upper_shadow = data.high - max(data.open, data.close)  # 上影线长度
        lower_shadow = min(data.open, data.close) - data.low   # 下影线长度
        
        # 判断是否为阳线（收盘价高于开盘价）
        is_bullish = data.close > data.open
        
        # 锤子线形态判断条件
        is_hammer = (
            lower_shadow >= body * self.min_lower_shadow and  # 下影线长度要求
            upper_shadow <= body * self.max_upper_shadow and  # 上影线长度要求
            is_bullish and  # 阳线
            in_downtrend  # 处于下跌趋势
        )
        
        # 返回检测结果
        return PatternResult(
            pattern_name="Hammer",  # 形态名称：锤子线
            is_detected=is_hammer,  # 是否检测到锤子线
            datetime=data.datetime,  # 时间戳
            additional_info={       # 额外信息
                "body": body,                    # 实体长度
                "upper_shadow": upper_shadow,    # 上影线长度
                "lower_shadow": lower_shadow,    # 下影线长度
                "is_bullish": is_bullish,        # 是否为阳线
                "in_downtrend": in_downtrend,    # 是否处于下跌趋势
            }
        )