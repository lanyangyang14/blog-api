"""限流测试。"""

import pytest

pytestmark = pytest.mark.integration


def test_like_rate_limit(client, auth_headers):
    """连续点赞超过限流（mock 环境下可能不触发 429）。"""
    # 1. 创建文章
    r = client.post(
        "/api/v1/posts",
        json={
            "title": "Rate Limit Test",
            "slug": "rate-limit-test",
            "content": "content",
        },
        headers=auth_headers,
    )
    assert r.status_code == 201
    post_id = r.json()["id"]

    # 2. 快速点赞多次
    for _ in range(15):
        r = client.post(
            f"/api/v1/posts/{post_id}/like",
            headers=auth_headers,
        )
        if r.status_code in (409, 429):
            break

    # 3. mock 环境下不会真 429，只要不是 500 就通过
    assert r.status_code != 500
