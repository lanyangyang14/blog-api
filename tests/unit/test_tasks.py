"""Celery 任务测试。"""


def test_send_welcome_email_task():
    """欢迎邮件任务（同步执行）。"""
    from blog_api.tasks.email import send_welcome_email

    result = send_welcome_email.apply(
        kwargs={"user_id": 1, "email": "test@example.com", "username": "test"}
    )
    assert result.successful()
    assert result.result["status"] == "ok"


def test_send_email_task():
    """邮件任务。"""
    from blog_api.tasks.email import send_email

    result = send_email.apply(kwargs={"to": "test@example.com", "subject": "Test", "body": "Hello"})
    assert result.successful()
    assert result.result["status"] == "ok"


def test_notify_new_post_task():
    """通知任务。"""
    from blog_api.tasks.notification import notify_new_post

    result = notify_new_post.apply(
        kwargs={
            "post_id": 1,
            "title": "Test",
            "slug": "test",
            "author_name": "alice",
        }
    )
    assert result.successful()
    assert result.result["status"] == "ok"


def test_cleanup_post_data_task():
    """清理任务。"""
    from blog_api.tasks.notification import cleanup_post_data

    result = cleanup_post_data.apply(kwargs={"post_id": 1})
    assert result.successful()
    assert result.result["status"] == "ok"


def test_generate_daily_report_task():
    """报表任务。"""
    from blog_api.tasks.report import generate_daily_report

    result = generate_daily_report.apply()
    assert result.successful()
    assert result.result["status"] == "ok"
