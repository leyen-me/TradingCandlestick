import os

SYMBOL = "TSLA.US"

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