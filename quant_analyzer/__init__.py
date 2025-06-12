import logging
import backtrader as bt
import pandas as pd
from db import CandlestickDataManager
from config import SYMBOL, PERIOD
from patterns import BasePatternDetector
from patterns import HammerPatternDetector
from patterns import DojiPatternDetector
from patterns import InvertedHammerPatternDetector

logger = logging.getLogger(__name__)
class MyStrategy(bt.Strategy):
    def __init__(self):
        self.base_detector = BasePatternDetector()
        self.hammer_detector = HammerPatternDetector()
        self.doji_detector = DojiPatternDetector()
        self.inverted_hammer_detector = InvertedHammerPatternDetector()
        self.order = None  # 跟踪订单
    
    def next(self):
        is_downtrend = self.base_detector.is_downtrend()

        self.base_detector.update_candles(self.data)

        res1 = self.hammer_detector.detect(self.data)
        res2 = self.doji_detector.detect(self.data)
        res3 = self.inverted_hammer_detector.detect(self.data)
        
        # 检查是否已经持有仓位
        if is_downtrend and (res1.is_detected or res2.is_detected or res3.is_detected) and self.position.size <= 0:
            # 计算买入价格
            price = self.data.close[0]
            # 计算止损价格（下跌0.5%）
            stop_price = price * (1 - 0.0035)
            # 计算止盈价格（上涨0.5%）
            limit_price = price * (1 + 0.0035)
            
            # 计算仓位大小（使用总资金的80%）
            cash_to_use = self.broker.getcash() * 0.8
            size = int(cash_to_use / price)
            
            if size > 0:  # 确保有足够的资金进行交易
                # 执行买入订单
                self.order = self.buy_bracket(limitprice=limit_price, stopprice=stop_price, size=size)
                self.log(f'发出买入信号: 价格: {price:.2f}, 数量: {size}, 止损: {stop_price:.2f}, 止盈: {limit_price:.2f}')

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # 订单已提交或已接受，等待执行
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'买入执行: 价格: {order.executed.price:.2f}, 数量: {order.executed.size}, 手续费: {order.executed.comm:.2f}')
            else:
                self.log(f'卖出执行: 价格: {order.executed.price:.2f}, 数量: {order.executed.size}, 手续费: {order.executed.comm:.2f}')
            self.order = None  # 重置订单状态
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log(f'订单失败: {order.getstatusname()}')
            self.order = None  # 重置订单状态
        elif order.status in [order.Partial]:
            self.log(f'订单部分成交: 价格: {order.executed.price:.2f}, 数量: {order.executed.size}')

    def log(self, txt, dt=None):
        dt = dt or self.data.datetime.datetime()
        print(f'{dt.strftime("%Y-%m-%d %H:%M:%S")} {txt}')


def run():
    start_cash = 100000.0
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
    cerebro.broker.setcash(start_cash)

    # 设置交易手续费
    cerebro.broker.setcommission(commission=0.001)

    # 运行回测
    cerebro.run()

    # 打印最终资金
    print('最终资金: ', cerebro.broker.getcash())
    if start_cash > cerebro.broker.getcash():
        print(f'亏损: {start_cash - cerebro.broker.getcash():.2f}')
    else:
        print(f'盈利: {cerebro.broker.getcash() - start_cash:.2f}')
    

    # 绘制结果
    cerebro.plot(
        style='candle', # 使用蜡烛图样式
        barup='red', # 上涨蜡烛颜色
        bardown='green', # 下跌蜡烛颜色
        volume=False, # 不显示成交量
    )