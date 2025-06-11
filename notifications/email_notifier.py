import yagmail
import logging
from datetime import datetime, timedelta
from config import QQ_SMTP_SERVER, QQ_SMTP_PORT, QQ_SENDER_EMAIL, QQ_SENDER_PASSWORD, QQ_RECEIVER_EMAIL

class EmailNotifier:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.last_email_time = None
        self.email_cooldown = timedelta(minutes=5)  # 邮件发送冷却时间
        
        # 初始化yagmail SMTP客户端
        try:
            self.yag = yagmail.SMTP(
                user=QQ_SENDER_EMAIL,
                password=QQ_SENDER_PASSWORD,
                host=QQ_SMTP_SERVER,
                port=QQ_SMTP_PORT,
                smtp_ssl=True,
                smtp_starttls=False
            )
            self.logger.info("邮件客户端初始化成功")
        except Exception as e:
            self.logger.error(f"邮件客户端初始化失败: {e}")
            self.yag = None

    def send_email(self, subject: str, content: str) -> bool:
        """
        发送邮件通知
        
        Args:
            subject: 邮件主题
            content: 邮件内容
            
        Returns:
            bool: 发送是否成功
        """
        try:
            if self.yag:
                self.yag.send(to=QQ_RECEIVER_EMAIL,
                            subject=subject, 
                            contents=content)
                self.logger.info(f"成功发送邮件通知: {subject}")
                return True
            else:
                self.logger.error("邮件客户端未初始化")
                return False

        except Exception as e:
            self.logger.error(f"发送邮件失败: {e}")
            return False 