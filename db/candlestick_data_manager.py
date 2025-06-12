from datetime import datetime
from config import PERIOD
from db.db_manager import DBManager
from longport.openapi import PushCandlestick


class CandlestickDataManager:
    
    def __init__(self):
        self.db_manager = DBManager()
    
    # 保存K线数据
    def save_candlestick_data(self, symbol: str, event: PushCandlestick):
        sql = """
                INSERT INTO t_candlesticks (
                    stock_code, period, is_confirmed, open, high, low, close, volume, turnover,
                    timestamp
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
        
        params = (
                        symbol, PERIOD, event.is_confirmed, event.candlestick.open, 
                        event.candlestick.high, event.candlestick.low, event.candlestick.close, 
                        event.candlestick.volume, event.candlestick.turnover, 
                        event.candlestick.timestamp
                    )
        self.db_manager.save(sql, params)
    
    def get_candlestick_data(self, symbol: str, period: str = PERIOD):
        sql = """
                SELECT open, high, low, close, volume, turnover, timestamp 
                FROM t_candlesticks 
                WHERE stock_code = %s AND period = %s 
                ORDER BY timestamp ASC
                """
        params = (symbol, period)
        results = self.db_manager.query(sql, params)
        
        # 转换时间戳
        formatted_results = []
        for row in results:
            row_dict = dict(row)
            if isinstance(row_dict['timestamp'], (int, float)):
                row_dict['timestamp'] = datetime.fromtimestamp(row_dict['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            formatted_results.append(row_dict)
            
        return formatted_results
    