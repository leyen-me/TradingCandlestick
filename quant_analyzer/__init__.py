import backtrader as bt
import pandas as pd
from datetime import datetime
from db import CandlestickDataManager
from config import SYMBOL, PERIOD
from patterns import HammerPatternDetector
from patterns import DojiPatternDetector
from patterns import InvertedHammerPatternDetector
class MyStrategy(bt.Strategy):
    def __init__(self):
        self.hammer_detector = HammerPatternDetector()
        self.doji_detector = DojiPatternDetector()
        self.inverted_hammer_detector = InvertedHammerPatternDetector()
    
    def next(self):
        res = self.hammer_detector.detect(self.data)
        if res.is_detected:
            self.buy(size=0.1)

    def close(self):
        self.sell()

def run():
    # 创建 Cerebro 引擎
    cerebro = bt.Cerebro()
    candlestick_data_manager = CandlestickDataManager()

    # 获取数据
    data = candlestick_data_manager.get_candlestick_data(SYMBOL, PERIOD)
    
    # 将元组数据转换为DataFrame
    df = pd.DataFrame(data, columns=[
        'id', 'stock_code', 'period', 'is_confirmed', 
        'open', 'high', 'low', 'close', 'volume', 
        'turnover', 'timestamp'
    ])
    
    # 将timestamp列转换为datetime类型
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # 创建backtrader数据源
    data = bt.feeds.PandasData(
        dataname=df,
        datetime='timestamp',
        open='open',
        high='high',
        low='low',
        close='close',
        volume='volume',
        openinterest=-1  # 不使用持仓量
    )
    
    # 添加数据
    cerebro.adddata(data)

    # 添加策略
    cerebro.addstrategy(MyStrategy)

    # 设置初始资金
    cerebro.broker.setcash(100000.0)

    # 设置交易手续费
    cerebro.broker.setcommission(commission=0.001)

    # 运行回测
    cerebro.run()

    # 打印最终资金
    print(f'最终资金: {cerebro.broker.getvalue():.2f}')

    # 绘制结果
    cerebro.plot(
        style='candle', # 使用蜡烛图样式
        barup='red', # 上涨蜡烛颜色
        bardown='green', # 下跌蜡烛颜色
        volume=False, # 不显示成交量
    )