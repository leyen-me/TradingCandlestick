import logging
import pymysql
from config import DB_CONFIG

logger = logging.getLogger(__name__)

class DBManager:
    
    def __init__(self):
        pass

    # 初始化数据库连接
    def get_db_connection(self):
        try:
            conn = pymysql.connect(**DB_CONFIG)
            return conn
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            logger.error("错误详情:", exc_info=True)
            raise
    
    # 保存数据
    def save(self, sql, params):
        try:
            conn = self.get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
            conn.commit()
        except Exception as e:
            logger.error(f"保存数据时出错: {e}")
            logger.error("错误详情:", exc_info=True)
        finally:
            try:
                conn.close()
            except:
                logger.warning("关闭数据库连接时发生错误")
    
    # 查询数据
    def query(self, sql, params):
        try:
            conn = self.get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"查询数据时出错: {e}")
            logger.error("错误详情:", exc_info=True)
            raise