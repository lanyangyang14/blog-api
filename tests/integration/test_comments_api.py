"""Comment API 测试。"""

import pytest
import pytest_asyncio

pytestmark = pytest.mark.integration


@pytest_asyncio.fixture
async def post_id(client, auth_headers):
    """创建一篇文章，返回 id。"""
    response = await client.post(
        "/api/v1/posts",
        json={
            "title": "Test Post",
            "slug": "test-post",
            "content": "content",
            "status": "published",
        },
        headers=auth_headers,
    )
    return response.json()["id"]


async def test_create_comment(client, auth_headers, post_id):
    response = await client.post(
        f"/api/v1/posts/{post_id}/comments",
        json={"content": "Nice post!"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    assert response.json()["content"] == "Nice post!"


async def test_nested_comment(client, auth_headers, post_id):
    # 一级评论
    r = await client.post(
        f"/api/v1/posts/{post_id}/comments",
        json={"content": "first"},
        headers=auth_headers,
    )
    parent_id = r.json()["id"]

    # 二级回复
    r = await client.post(
        f"/api/v1/posts/{post_id}/comments",
        json={"content": "reply", "parent_id": parent_id},
        headers=auth_headers,
    )
    assert r.status_code == 201
    assert r.json()["parent_id"] == parent_id


async def test_list_comments_tree(client, auth_headers, post_id):
    r = await client.post(
        f"/api/v1/posts/{post_id}/comments",
        json={"content": "parent"},
        headers=auth_headers,
    )
    parent_id = r.json()["id"]
    await client.post(
        f"/api/v1/posts/{post_id}/comments",
        json={"content": "child", "parent_id": parent_id},
        headers=auth_headers,
    )

    r = await client.get(f"/api/v1/posts/{post_id}/comments")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1
    assert len(data[0]["replies"]) == 1


async def test_update_comment(client, auth_headers, post_id):
    r = await client.post(
        f"/api/v1/posts/{post_id}/comments",
        json={"content": "old"},
        headers=auth_headers,
    )
    comment_id = r.json()["id"]

    r = await client.put(
        f"/api/v1/comments/{comment_id}",
        json={"content": "new"},
        headers=auth_headers,
    )
    assert r.status_code == 200
    assert r.json()["content"] == "new"


async def test_delete_comment(client, auth_headers, post_id):
    r = await client.post(
        f"/api/v1/posts/{post_id}/comments",
        json={"content": "delete me"},
        headers=auth_headers,
    )
    comment_id = r.json()["id"]

    r = await client.delete(f"/api/v1/comments/{comment_id}", headers=auth_headers)
    assert r.status_code == 204

    # 列表里 is_deleted=True
    r = await client.get(f"/api/v1/posts/{post_id}/comments")
    # 软删除的评论不在树里（默认过滤）
