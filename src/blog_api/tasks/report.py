"""报表任务（占位）。"""

import logging
import time

from blog_api.core.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="tasks.generate_daily_report")
def generate_daily_report() -> dict:
    """生成每日报表（模拟）。"""
    logger.info("开始生成日报")
    time.sleep(3)
    logger.info("日报生成完成")
    return {"status": "ok", "report": "daily_report.pdf"}


@celery_app.task(name="tasks.cleanup_expired_data")
def cleanup_expired_data(days: int = 30) -> dict:
    """清理过期数据（模拟）。"""
    logger.info("清理 %d 天前的数据", days)
    return {"status": "ok", "deleted": 0}
