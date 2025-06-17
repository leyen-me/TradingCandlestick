import logging
from datetime import datetime
from longport.openapi import Config, QuoteContext, Period, PushCandlestick
from flask import Flask, jsonify
from flask_cors import CORS
from config import SYMBOL

from db import CandlestickDataManager
from patterns import HammerPatternDetector
from patterns import DojiPatternDetector
from patterns import InvertedHammerPatternDetector
from notifications import EmailNotifier


logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

hammer_detector = HammerPatternDetector()
doji_detector = DojiPatternDetector()
inverted_hammer_detector = InvertedHammerPatternDetector()
candlestick_data_manager = CandlestickDataManager()
email_notifier = EmailNotifier()

def on_candlestick(symbol: str, event: PushCandlestick):
    # 保存K线数据到数据库
    candlestick_data_manager.save_candlestick_data(symbol, event)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/candlestick')
def candlestick():
    return jsonify(candlestick_data_manager.get_candlestick_data(SYMBOL))

config = Config.from_env()
quote_ctx = QuoteContext(config)

quote_ctx.set_on_candlestick(on_candlestick)
quote_ctx.subscribe_candlesticks(SYMBOL, Period.Min_2)

logger.info("启动成功，当前北京时间：%s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
app.run(host='0.0.0.0', port=80, debug=True)