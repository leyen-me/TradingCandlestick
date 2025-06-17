from .candle_data import CandleData
from .pattern_result import PatternResult
import logging

logger = logging.getLogger(__name__)

class HammerPatternDetector:

    """锤子线形态检测器"""
    def __init__(self):
        self.min_lower_shadow = 0.6
        self.max_upper_shadow = 1.5

    def detect(self, data: CandleData) -> PatternResult:
        """
        检测当前K线是否形成锤子线形态
        """
        # 计算K线各组成部分
        body = abs(data.close - data.open)                     # 实体长度
        upper_shadow = data.high - max(data.open, data.close)  # 上影线长度
        lower_shadow = min(data.open, data.close) - data.low   # 下影线长度
        
        # 锤子线形态判断条件
        is_hammer = (
            lower_shadow >= body * self.min_lower_shadow and  # 下影线长度要求
            upper_shadow <= body * self.max_upper_shadow  # 上影线长度要求
        )
        
        # 返回检测结果
        return PatternResult(
            pattern_name="Hammer",  # 形态名称：锤子线
            pattern_desc="锤子形态",
            is_detected=is_hammer  # 是否检测到锤子线
        )