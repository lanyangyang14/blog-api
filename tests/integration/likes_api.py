"""Like API 测试。"""

import pytest
import pytest_asyncio

pytestmark = pytest.mark.integration


@pytest_asyncio.fixture
async def post_id(client, auth_headers):
    response = await client.post(
        "/api/v1/posts",
        json={
            "title": "Like Test",
            "slug": "like-test",
            "content": "content",
        },
        headers=auth_headers,
    )
    return response.json()["id"]


async def test_like_post(client, auth_headers, post_id):
    r = await client.post(f"/api/v1/posts/{post_id}/like", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["is_liked"] is True
    assert r.json()["like_count"] == 1


async def test_like_twice(client, auth_headers, post_id):
    await client.post(f"/api/v1/posts/{post_id}/like", headers=auth_headers)
    r = await client.post(f"/api/v1/posts/{post_id}/like", headers=auth_headers)
    assert r.status_code == 409


async def test_unlike(client, auth_headers, post_id):
    await client.post(f"/api/v1/posts/{post_id}/like", headers=auth_headers)
    r = await client.delete(f"/api/v1/posts/{post_id}/like", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["is_liked"] is False
    assert r.json()["like_count"] == 0


async def test_get_like_status(client, auth_headers, post_id):
    r = await client.get(f"/api/v1/posts/{post_id}/like", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["is_liked"] is False
