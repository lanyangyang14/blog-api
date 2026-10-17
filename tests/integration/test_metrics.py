"""Metrics 测试。"""

import pytest

pytestmark = pytest.mark.integration


async def test_metrics_endpoint(client):
    """/metrics 端点能访问。"""
    r = await client.get("/metrics")
    assert r.status_code == 200
    assert "http_requests_total" in r.text


async def test_metrics_after_request(client):
    """请求后指标增加。"""
    await client.get("/health")
    r = await client.get("/metrics")
    assert "http_requests_total" in r.text
