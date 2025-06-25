import time
import logging
import threading
from datetime import datetime
from collections import OrderedDict
from decimal import ROUND_DOWN, ROUND_UP, Decimal

from longport.openapi import Config, QuoteContext, TradeContext, PushOrderChanged, OrderType, OrderStatus
from longport.openapi import OrderSide, TimeInForceType, Period, AdjustType, TradeSessions, TopicType

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

config = Config.from_env()
quote_ctx = QuoteContext(config)
trade_ctx = TradeContext(config)

resp = quote_ctx.candlesticks("TSLA.US", Period.Min_2, 1000, AdjustType.NoAdjust, TradeSessions.Intraday)

with open("kline_data.csv", "w", encoding="utf-8") as f:
    f.write("time,open,high,low,close,volume\n")
    for item in resp:
        line = f"{item.timestamp.strftime('%Y-%m-%d %H:%M:%S')},{float(item.open)},{float(item.high)},{float(item.low)},{float(item.close)},{float(item.volume)}\n"
        f.write(line)