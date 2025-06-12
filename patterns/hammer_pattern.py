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
    def __init__(self, min_lower_shadow: float = 0.6, max_upper_shadow: float = 1.5):
        """
        初始化锤子线检测器
        
        参数:
            min_lower_shadow: 下影线最小长度（相对于实体）
            max_upper_shadow: 上影线最大长度（相对于实体）
        """
        self.min_lower_shadow = min_lower_shadow
        self.max_upper_shadow = max_upper_shadow

    def detect(self, data: CandleData) -> PatternResult:
        """
        检测当前K线是否形成锤子线形态
        
        参数:
            data: CandleData对象，包含K线数据
            
        返回:
            PatternResult对象，包含检测结果
        """
        # 计算K线各组成部分
        body = abs(data.close - data.open)                     # 实体长度
        upper_shadow = data.high - max(data.open, data.close)  # 上影线长度
        lower_shadow = min(data.open, data.close) - data.low   # 下影线长度
        
        # 判断是否为阳线（收盘价高于开盘价）
        is_bullish = data.close > data.open
        
        # 锤子线形态判断条件
        is_hammer = (
            lower_shadow >= body * self.min_lower_shadow and  # 下影线长度要求
            upper_shadow <= body * self.max_upper_shadow and  # 上影线长度要求
            is_bullish                                        # 阳线
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
            }
        )