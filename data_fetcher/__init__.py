import time
import logging
from datetime import datetime
from longport.openapi import Config, QuoteContext, Period, PushCandlestick

from config import SYMBOL

from db import CandlestickDataManager
from patterns import HammerPatternDetector
from patterns import DojiPatternDetector
from patterns import InvertedHammerPatternDetector
from notifications import EmailNotifier


logger = logging.getLogger(__name__)

hammer_detector = HammerPatternDetector()
doji_detector = DojiPatternDetector()
inverted_hammer_detector = InvertedHammerPatternDetector()
candlestick_data_manager = CandlestickDataManager()
email_notifier = EmailNotifier()

def on_candlestick(symbol: str, event: PushCandlestick):
    
    # 如果K线未确认，则不进行处理
    if not event.is_confirmed:
        return
    
    # 保存K线数据到数据库
    candlestick_data_manager.save_candlestick_data(symbol, event)
    
    # 检测锤子线形态
    # hammer_result = hammer_detector.detect(event.candlestick)
    # 检测十字星形态
    # doji_result = doji_detector.detect(event.candlestick)
    # 检测倒垂线形态
    # inverted_hammer_result = inverted_hammer_detector.detect(event.candlestick)
    
    # # 如果检测到锤子线形态，发送邮件通知
    # if hammer_result.is_detected:
    #     logger.info(f"检测到锤子线形态 - {symbol}, 置信度: {hammer_result.confidence:.2%}")
    #     logger.info(f"趋势强度: {hammer_result.additional_info['trend_strength']:.2%}")
    #     email_notifier.send_email(f"锤子线形态检测 - {symbol}", hammer_result)
    
    # # 如果检测到十字星形态，发送邮件通知
    # if doji_result.is_detected:
    #     logger.info(f"检测到十字星形态 - {symbol}, 置信度: {doji_result.confidence:.2%}")
    #     logger.info(f"趋势强度: {doji_result.additional_info['trend_strength']:.2%}")
    #     email_notifier.send_email(f"十字星形态检测 - {symbol}", doji_result)
    
    # # 如果检测到倒垂线形态，发送邮件通知
    # if inverted_hammer_result.is_detected:
    #     logger.info(f"检测到倒垂线形态 - {symbol}, 置信度: {inverted_hammer_result.confidence:.2%}")
    #     logger.info(f"趋势强度: {inverted_hammer_result.additional_info['trend_strength']:.2%}")
    #     email_notifier.send_email(f"倒垂线形态检测 - {symbol}", inverted_hammer_result)


def run():
    config = Config.from_env()
    quote_ctx = QuoteContext(config)

    quote_ctx.set_on_candlestick(on_candlestick)
    quote_ctx.subscribe_candlesticks(SYMBOL, Period.Min_2)

    try:
        logger.info("开始运行主循环")
        logger.info(f"服务启动成功，当前时间为北京时间: {datetime.now()}")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("程序被用户中断")
    except Exception as e:
        logger.error(f"程序运行出错: {e}")