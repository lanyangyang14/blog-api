"""通知任务。"""

import logging

from blog_api.core.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    name="tasks.notify_new_post",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def notify_new_post(
    self,
    post_id: int,
    title: str,
    slug: str,
    author_name: str,
) -> dict:
    """通知订阅者有新文章（模拟）。"""
    try:
        logger.info(
            "通知订阅者: post_id=%s, title=%s, author=%s",
            post_id,
            title,
            author_name,
        )
        # 模拟发送通知
        # 真实实现：查订阅者 → 发邮件/推送
        # subscribers = get_subscribers(author_name)
        # for sub in subscribers:
        #     send_email.delay(to=sub.email, subject=f"新文章: {title}", body=...)

        return {
            "status": "ok",
            "post_id": post_id,
            "title": title,
            "slug": slug,
        }
    except Exception as exc:
        logger.exception("通知失败: post_id=%s", post_id)
        raise self.retry(exc=exc) from exc


@celery_app.task(name="tasks.cleanup_post_data")
def cleanup_post_data(post_id: int) -> dict:
    """清理文章关联数据（模拟）。"""
    logger.info("清理文章关联数据: post_id=%s", post_id)
    # 真实实现：删缓存、删文件、删评论等
    return {"status": "ok", "post_id": post_id}
