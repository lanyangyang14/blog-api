"""邮件任务。"""

import logging
import time

from blog_api.core.celery_app import celery_app
from blog_api.logging_config import set_trace_id

logger = logging.getLogger(__name__)


def _send_email_impl(to: str, subject: str, body: str) -> dict:
    """发邮件的实际实现（同步）。"""
    logger.info("发送邮件: to=%s, subject=%s", to, subject)
    time.sleep(2)  # 模拟耗时
    logger.info("邮件发送成功: to=%s", to)
    return {"status": "ok", "to": to, "subject": subject}


@celery_app.task(
    name="tasks.send_email",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def send_email(self, to: str, subject: str, body: str) -> dict:
    """发送邮件。"""
    try:
        return _send_email_impl(to, subject, body)
    except Exception as exc:
        logger.exception("邮件发送失败: to=%s", to)
        raise self.retry(exc=exc) from exc


@celery_app.task(name="tasks.send_welcome_email")
def send_welcome_email(user_id: int, email: str, username: str, trace_id: str = "-") -> dict:
    """发送欢迎邮件（直接发，不嵌套任务）。"""
    if trace_id != "-":
        set_trace_id(trace_id)
    subject = "欢迎注册"
    body = f"你好 {username}！感谢注册。"
    return _send_email_impl(to=email, subject=subject, body=body)
