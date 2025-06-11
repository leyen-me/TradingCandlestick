import time
import pymysql
from datetime import datetime
from longport.openapi import Config, QuoteContext
from longport.openapi import SubType, Period, PushCandlestick
from longport.openapi import PushQuote, PushTrades, PushDepth
from config import SYMBOL
from dotenv import load_dotenv
import os
import logging
from patterns.hammer_pattern import HammerPatternDetector
from patterns.doji_pattern import DojiPatternDetector
from patterns.inverted_hammer_pattern import InvertedHammerPatternDetector
from notifications.email_notifier import EmailNotifier

# 配置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)



# 加载环境变量
load_dotenv()
logger.info("环境变量加载完成")

# 初始化模式检测器和邮件通知器
hammer_detector = HammerPatternDetector()
doji_detector = DojiPatternDetector()
inverted_hammer_detector = InvertedHammerPatternDetector()
email_notifier = EmailNotifier()

# 数据库配置
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'db': os.getenv('DB_NAME', 'trading_data'),
    'charset': 'utf8mb4',
    'connect_timeout': 10,  # 连接超时时间（秒）
    'read_timeout': 10,     # 读取超时时间（秒）
    'write_timeout': 10,    # 写入超时时间（秒）
    'autocommit': True      # 自动提交事务
}

logger.info(
    f"数据库配置: host={DB_CONFIG['host']}, user={DB_CONFIG['user']}, db={DB_CONFIG['db']}")

# 初始化数据库连接
def get_db_connection():
    try:
        conn = pymysql.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        logger.error(f"数据库连接失败: {e}")
        logger.error("错误详情:", exc_info=True)
        raise

def save_candlestick_data(symbol: str, event: PushCandlestick):
    try:
        # 保存K线数据到数据库
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = """
            INSERT INTO t_candlesticks (
                stock_code, period, is_confirmed, open, high, low, close, volume, turnover,
                timestamp
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                    symbol, 'Min_2', event.is_confirmed, event.candlestick.open, 
                    event.candlestick.high, event.candlestick.low, event.candlestick.close, 
                    event.candlestick.volume, event.candlestick.turnover, 
                    event.candlestick.timestamp
                ))
        conn.commit()
    except Exception as e:
        logger.error(f"处理K线数据时出错: {e}")
        logger.error("错误详情:", exc_info=True)
    finally:
        try:
            conn.close()
        except:
            logger.warning("关闭数据库连接时发生错误")

logger.info("开始初始化 Longport API...")
config = Config.from_env()
logger.info("Longport API 配置完成")

logger.info("开始创建 QuoteContext...")
quote_ctx = QuoteContext(config)
logger.info("QuoteContext 创建完成")

def on_candlestick(symbol: str, event: PushCandlestick):
    
    # 保存K线数据到数据库
    save_candlestick_data(symbol, event)
    
    # 检测锤子线形态
    hammer_result = hammer_detector.detect(
        open_price=event.candlestick.open,
        high=event.candlestick.high,
        low=event.candlestick.low,
        close=event.candlestick.close,
        volume=event.candlestick.volume,
        symbol=symbol,
        timestamp=event.candlestick.timestamp
    )
    
    # 检测十字星形态
    doji_result = doji_detector.detect(
        open_price=event.candlestick.open,
        high=event.candlestick.high,
        low=event.candlestick.low,
        close=event.candlestick.close,
        volume=event.candlestick.volume,
        symbol=symbol,
        timestamp=event.candlestick.timestamp
    )
    
    # 检测倒垂线形态
    inverted_hammer_result = inverted_hammer_detector.detect(
        open_price=event.candlestick.open,
        high=event.candlestick.high,
        low=event.candlestick.low,
        close=event.candlestick.close,
        volume=event.candlestick.volume,
        symbol=symbol,
        timestamp=event.candlestick.timestamp
    )
    
    # 如果检测到锤子线形态，发送邮件通知
    if hammer_result.is_detected:
        logger.info(f"检测到锤子线形态 - {symbol}, 置信度: {hammer_result.confidence:.2%}")
        logger.info(f"趋势强度: {hammer_result.additional_info['trend_strength']:.2%}")
        email_notifier.send_email(f"锤子线形态检测 - {symbol}", hammer_result)
    
    # 如果检测到十字星形态，发送邮件通知
    if doji_result.is_detected:
        logger.info(f"检测到十字星形态 - {symbol}, 置信度: {doji_result.confidence:.2%}")
        logger.info(f"趋势强度: {doji_result.additional_info['trend_strength']:.2%}")
        email_notifier.send_email(f"十字星形态检测 - {symbol}", doji_result)
    
    # 如果检测到倒垂线形态，发送邮件通知
    if inverted_hammer_result.is_detected:
        logger.info(f"检测到倒垂线形态 - {symbol}, 置信度: {inverted_hammer_result.confidence:.2%}")
        logger.info(f"趋势强度: {inverted_hammer_result.additional_info['trend_strength']:.2%}")
        email_notifier.send_email(f"倒垂线形态检测 - {symbol}", inverted_hammer_result)

quote_ctx.set_on_candlestick(on_candlestick)
quote_ctx.subscribe_candlesticks(SYMBOL, Period.Min_2)
logger.info("Candlesticks 订阅完成")

try:
    logger.info("开始运行主循环")
    logger.info(f"服务启动成功，当前时间为北京时间: {datetime.now()}")
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    logger.info("程序被用户中断")
except Exception as e:
    logger.error(f"程序运行出错: {e}")