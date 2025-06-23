from decimal import ROUND_DOWN, ROUND_UP, Decimal
import logging
from datetime import datetime
from longport.openapi import Config, QuoteContext, TradeContext, PushOrderChanged, OrderStatus, OrderType
from longport.openapi import Period, PushCandlestick, PushQuote, SubType, TopicType, OrderSide, TimeInForceType
from flask import Flask, jsonify, request
from flask_socketio import SocketIO

from config import SYMBOL
from db import CandlestickDataManager
from utils import setup_logging, setup_dotenv
from patterns import CandleData
from patterns import HammerPatternDetector
from patterns import DojiPatternDetector
from patterns import InvertedHammerPatternDetector
from notifications import EmailNotifier

setup_logging()
setup_dotenv()

logger = logging.getLogger(__name__)

app = Flask(__name__)
socketio = SocketIO(app)

patterns = [
    HammerPatternDetector(),
    # DojiPatternDetector(),
    # InvertedHammerPatternDetector()
]
candlestick_data_manager = CandlestickDataManager()
email_notifier = EmailNotifier()
config = Config.from_env()
quote_ctx = QuoteContext(config)
trade_ctx = TradeContext(config)

def on_order_changed(event: PushOrderChanged):
    if str(event.side) == "OrderSide.Buy" and  str(event.status) == "OrderStatus.Filled":
        print("======================有新的买入订单======================")
        # 当新订单提交完成之后，手动为用户设置止损
        trade_ctx.submit_order(
            event.symbol,
            OrderType.MIT,
            OrderSide.Sell,
            event.executed_quantity,
            TimeInForceType.GoodTilCanceled,
            trigger_price=event.submitted_price * Decimal('0.9').quantize(Decimal('0.01'), rounding=ROUND_DOWN),
            remark="程序止损",
        )

def on_quote(symbol: str, event: PushQuote):
    if event.current_volume == 0:
       return
    candlestick_data_manager.save_quote_data(symbol, event)

def on_candlestick(symbol: str, event: PushCandlestick):
    if event.candlestick.volume == 0:
       return
    # 保存K线数据到数据库
    candlestick_data_manager.save_candlestick_data(symbol, event)
    socketio.emit('candlestick', {'symbol': symbol, 'data': {
        'open': float(event.candlestick.open),
        'high': float(event.candlestick.high),
        'low': float(event.candlestick.low),
        'close': float(event.candlestick.close),
        'volume': float(event.candlestick.volume),
        'turnover': float(event.candlestick.turnover),
        'time': event.candlestick.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    }})

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/candlestick', methods=["POST"])
def candlestick():
    parmas = request.json
    time = parmas['time']
    startTime = parmas['startTime']
    endTime = parmas['endTime']
    if time == "realtime":
        return jsonify(candlestick_data_manager.get_candlestick_data(SYMBOL, realtime=True, startTime=startTime, endTime=endTime))
    else:
        return jsonify(candlestick_data_manager.get_candlestick_data(SYMBOL, realtime=False, startTime=startTime, endTime=endTime))

@app.route('/api/pattern', methods=["POST"])
def pattern():
    parmas = request.json
    for pattern in patterns:
        pattern_res = pattern.detect(CandleData(open=parmas['open'], high=parmas['high'], low=parmas['low'], close=parmas['close']))
        if pattern_res.is_detected:
            return jsonify({
               "pattern_name":pattern_res.pattern_name,
               "pattern_desc":pattern_res.pattern_desc,
               "is_detected":pattern_res.is_detected
            })
    return jsonify({
        "is_detected": False
    })

quote_ctx.set_on_candlestick(on_candlestick)
quote_ctx.set_on_quote(on_quote)

trade_ctx.set_on_order_changed(on_order_changed)


quote_ctx.subscribe([SYMBOL], [SubType.Quote], is_first_push=True)
quote_ctx.subscribe_candlesticks(SYMBOL, Period.Min_2)

trade_ctx.subscribe([TopicType.Private])


logger.info("启动成功，当前北京时间：%s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
socketio.run(app, host='0.0.0.0', port=80, debug=True, allow_unsafe_werkzeug=True)