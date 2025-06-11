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

# 配置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()
logger.info("环境变量加载完成")

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


def save_quote_data(symbol: str, event: PushQuote):
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = """
            INSERT INTO t_quotes (
                stock_code, last_done, open, high, low, volume, turnover,
                trade_status, current_volume, current_turnover, timestamp
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                symbol, event.last_done, event.open, event.high, event.low,
                event.volume, event.turnover, event.trade_status,
                event.current_volume, event.current_turnover, datetime.now()
            ))
        conn.commit()
    except Exception as e:
        logger.error(f"保存行情数据失败: {e}")
        logger.error(f"错误详情: {str(e)}", exc_info=True)
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
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = """
            INSERT INTO t_candlesticks (
                stock_code, period, is_confirmed, open, high, low, close, volume, turnover,
                timestamp
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                    symbol, 'Min_2', event.is_confirmed, event.candlestick.open, event.candlestick.high, event.candlestick.low, event.candlestick.close, event.candlestick.volume, event.candlestick.turnover, event.candlestick.timestamp
                ))
        conn.commit()
    except Exception as e:
        print(f"Error saving candlestick data: {e}")
    finally:
        conn.close()

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