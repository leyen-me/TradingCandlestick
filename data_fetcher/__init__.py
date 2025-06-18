import logging
from datetime import datetime
from longport.openapi import Config, QuoteContext, TradeContext, Period, PushCandlestick
from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
from config import SYMBOL

from db import CandlestickDataManager

from patterns import CandleData
from patterns import HammerPatternDetector
from patterns import DojiPatternDetector
from patterns import InvertedHammerPatternDetector
from notifications import EmailNotifier


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





# quote_ctx.set_on_candlestick(on_candlestick)
quote_ctx.subscribe_candlesticks(SYMBOL, Period.Min_2)

logger.info("启动成功，当前北京时间：%s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
socketio.run(app, host='0.0.0.0', port=80, debug=True, allow_unsafe_werkzeug=True)