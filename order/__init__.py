from longport.openapi import QuoteContext, TradeContext, OrderType, OrderSide, TimeInForceType, OutsideRTH
import logging
from decimal import Decimal
import time

# ==================== Settings ====================
# 做多的ETF
DO_LONG_SYMBOL = "TSLL.US"
# 做空的ETF
DO_SHORT_SYMBOL = "TSDD.US"


# ==================== init ====================

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Action:
    BUY = "buy"
    SELL = "sell"

class Sentiment:
    LONG = "long"
    SHORT = "short"
    FLAT = "flat"

class Order:

    def __init__(self, t:TradeContext, q:QuoteContext) -> None:
        self.trade_ctx = t
        self.quote_ctx = q

    def get_current_price(self, action: Action, symbol: str):
        current_price = None
        resp = self.quote_ctx.depth(symbol)
        if resp.asks and resp.bids:
            if action == Action.BUY:
                if resp.asks[0].price is not None:
                    current_price = resp.asks[0].price  # 买入时参考卖一价
                else:
                    raise Exception("可能为夜盘，卖一价为空")
            elif action == Action.SELL:
                if resp.bids[0].price is not None:
                    current_price = resp.bids[0].price  # 卖出时参考买一价
                else:
                    raise Exception("可能为夜盘，买一价为空")
        else:
            raise Exception("当前无盘口数据...")
        return current_price


    def get_current_buy_price(self, symbol: str):
        return self.get_current_price(Action.BUY, symbol)

    def get_current_sell_price(self, symbol: str):
        return self.get_current_price(Action.SELL, symbol)

    def buy(self, symbol: str):
        try:
            current_price = self.get_current_buy_price(symbol)
            # 获取最大买入数量
            max_buy_resp = self.trade_ctx.estimate_max_purchase_quantity(
                symbol=symbol,
                order_type=OrderType.LO,
                side=OrderSide.Buy,
                price=current_price
            )
            logger.info(f"最大买入数量: {max_buy_resp.cash_max_qty}")
            # 90%的现金仓位
            quantity = int(int(max_buy_resp.cash_max_qty) * 0.9)
            self.trade_ctx.submit_order(
                symbol,
                OrderType.LO,
                OrderSide.Buy,
                Decimal(quantity),
                TimeInForceType.GoodTilCanceled,

                submitted_price=current_price,
                outside_rth=OutsideRTH.AnyTime,
                remark=f"{'多头' if DO_LONG_SYMBOL == symbol else '空头'}买入"
            )

            logger.info(f"买入订单执行完成 - 股票：{symbol}，数量：{quantity}")
        except Exception as e:
            logger.error(f"买入执行失败：{e}")


    def sell(self, symbol: str, quantity: int):
        try:
            current_price = self.get_current_sell_price(symbol)
            self.trade_ctx.submit_order(
                symbol,
                OrderType.LO,
                OrderSide.Sell,
                Decimal(quantity),
                TimeInForceType.GoodTilCanceled,

                submitted_price=current_price,
                outside_rth=OutsideRTH.AnyTime,
                remark=f"{'多头' if DO_LONG_SYMBOL == symbol else '空头'}卖出"
            )
            logger.info(f"卖出订单执行完成 - 股票：{symbol}，数量：{quantity}")
        except Exception as e:
            logger.error(f"卖出执行失败：{e}")


    def do_long(self):
        """
        做多
        """
        self.buy(DO_LONG_SYMBOL)
    

    def do_short(self):
        """
        做空
        """
        self.buy(DO_SHORT_SYMBOL)


    def do_close_position(self):
        """
        平仓
        """
        # 获取持仓信息
        stock_positions = []
        try:
            resp = self.trade_ctx.stock_positions()
            stock_positions = resp.channels
        except Exception as e:
            logger.error(f"获取持仓数量失败：{e}")

        # 平仓动作
        for channel in stock_positions:
            for position in channel.positions:
                if position.symbol == DO_LONG_SYMBOL or position.symbol == DO_SHORT_SYMBOL:
                    if position.quantity > 0 and position.quantity < 1:
                        # 碎骨单
                        logger.error(f"{position.symbol} 只剩碎骨单，不用平仓")
                    elif position.quantity <= 0:
                        logger.error(f"当前无多头/空头持仓")
                    else:
                        sell(position.symbol, position.quantity)
                else:
                    logger.error(f"当前无多头/空头持仓")
    
        # 每2秒循环检测持仓，直到用于没有任何持仓
        while True:
            time.sleep(2)
            resp = self.trade_ctx.stock_positions()
            stock_positions = resp.channels
            LONG_POSITION = False
            SHORT_POSITION = False
            for channel in stock_positions:
                for position in channel.positions:
                    if position.symbol == DO_LONG_SYMBOL and position.quantity > 1:
                        LONG_POSITION = True
                    elif position.symbol == DO_SHORT_SYMBOL and position.quantity > 1:
                        SHORT_POSITION = True
            
            # 两者同时没有持仓时，才算平仓完成
            if LONG_POSITION and SHORT_POSITION:
                continue
            else:
                break    