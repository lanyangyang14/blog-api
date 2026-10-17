"""Celery 应用"""

import os

from celery import Celery

from blog_api.config import settings
from blog_api.core.celery_beat_schedule import beat_schedule

celery_app = Celery(
    "blog_api",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "blog_api.tasks.email",
        "blog_api.tasks.notification",
        "blog_api.tasks.report",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    beat_schedule=beat_schedule,
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
    task_soft_time_limit=240,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
    result_expires=3600,
    # 测试环境同步执行
    task_always_eager=os.getenv("CELERY_TASK_ALWAYS_EAGER") == "true",
)
