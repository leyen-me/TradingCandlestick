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
                FROM t_candlesticks t1
                WHERE t1.stock_code = %s
                AND t1.period = %s
                AND t1.is_confirmed = 1
                AND t1.id = (
                    SELECT MAX(id)
                    FROM t_candlesticks t2
                    WHERE t2.stock_code = t1.stock_code
                        AND t2.period = t1.period
                        AND t2.timestamp = t1.timestamp
                )
                ORDER BY t1.timestamp ASC
                """
        params = (symbol, period)
        results = self.db_manager.query(sql, params)
        
        # 转换时间戳
        formatted_results = []
        for row in results:
            row_dict = dict(row)
            row_dict['time'] = row_dict['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            row_dict['open'] = float(row_dict['open'])
            row_dict['high'] = float(row_dict['high'])
            row_dict['low'] = float(row_dict['low'])
            row_dict['close'] = float(row_dict['close'])
            row_dict['volume'] = float(row_dict['volume'])
            row_dict['turnover'] = float(row_dict['turnover'])
            formatted_results.append(row_dict)
        
        return formatted_results
    