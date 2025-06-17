from dataclasses import dataclass

@dataclass
class PatternResult:
    """形态识别结果数据结构"""
    pattern_name: str    # 形态名称
    pattern_desc: str    # 形态中文描述
    is_detected: bool    # 是否检测到形态