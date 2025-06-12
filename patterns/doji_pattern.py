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

class DojiPatternDetector:
    """十字星形态检测器"""
    def __init__(self, body_ratio_threshold: float = 0.1):
        """
        初始化十字星检测器
        
        参数:
            body_ratio_threshold: 实体与总高度的最大比例（默认：0.1）
        """
        self.body_ratio_threshold = body_ratio_threshold
 
    def detect(self, data: CandleData) -> PatternResult:
        """
        检测当前K线是否形成十字星形态
        
        参数:
            data: CandleData对象，包含K线数据
            
        返回:
            PatternResult对象，包含检测结果
        """
        # 计算K线各组成部分
        body = abs(data.close - data.open)  # 实体长度
        total_height = data.high - data.low  # 总高度
        
        # 计算实体比例
        body_ratio = body / total_height if total_height > 0 else 0
        
        # 十字星形态判断条件
        is_doji = (
            body_ratio <= self.body_ratio_threshold
        )
        
        # 返回检测结果
        return PatternResult(
            pattern_name="Doji",  # 形态名称：十字星
            is_detected=is_doji,  # 是否检测到十字星
            datetime=data.datetime,  # 时间戳
            additional_info={       # 额外信息
                "body_ratio": body_ratio,    # 实体比例
                "body": body,                # 实体长度
                "total_height": total_height  # 总高度
            }
        ) 