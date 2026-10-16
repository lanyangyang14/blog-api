"""Celery Beat 定时任务。"""

from celery.schedules import crontab

# 定时任务配置
beat_schedule = {
    "cleanup-expired-data": {
        "task": "tasks.cleanup_expired_data",
        "schedule": crontab(hour=2, minute=0),  # 每天凌晨 2 点
        "args": (30,),  # 清理 30 天前的
    },
    "generate-daily-report": {
        "task": "tasks.generate_daily_report",
        "schedule": crontab(hour=8, minute=0),  # 每天早上 8 点
    },
}
