import os
from longport.openapi import Period



# ==================股票配置=====================
SYMBOL = "TSLA.US"



# ==================K线配置=====================
PERIOD = str(Period.Min_2)



# ==================邮件配置=====================
# 邮件配置
QQ_SMTP_SERVER = "smtp.qq.com"
# 邮件SSL端口
QQ_SMTP_PORT = 465
# 发送者
QQ_SENDER_EMAIL = "672228275@qq.com"
# QQ邮箱授权码
QQ_SENDER_PASSWORD = os.environ.get("QQ_SENDER_PASSWORD", "")
# 接收者
QQ_RECEIVER_EMAIL = "672228275@qq.com"



# ==================数据库配置=====================
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