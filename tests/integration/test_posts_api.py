"""Post API 集成测试。"""

import pytest

pytestmark = pytest.mark.integration


@pytest.fixture
def category(client, auth_headers):
    response = client.post(
        "/api/v1/categories",
        json={"name": "Tech", "slug": "tech"},
        headers=auth_headers,
    )
    return response.json()


@pytest.fixture
def tag(client, auth_headers):
    response = client.post(
        "/api/v1/tags",
        json={"name": "Python", "slug": "python"},
        headers=auth_headers,
    )
    return response.json()


def test_create_category(client, auth_headers):
    response = client.post(
        "/api/v1/categories",
        json={"name": "Tech", "slug": "tech"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Tech"


def test_create_post(client, auth_headers, category, tag):
    response = client.post(
        "/api/v1/posts",
        json={
            "title": "Hello World",
            "slug": "hello-world",
            "content": "This is my first post",
            "status": "published",
            "category_id": category["id"],
            "tag_ids": [tag["id"]],
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Hello World"
    assert data["slug"] == "hello-world"
    assert data["status"] == "published"
    assert data["category"]["name"] == "Tech"
    assert len(data["tags"]) == 1


def test_list_posts(client, auth_headers, category):
    # 创建两篇
    for i in range(2):
        client.post(
            "/api/v1/posts",
            json={
                "title": f"Post {i}",
                "slug": f"post-{i}",
                "content": f"content {i}",
                "status": "published",
                "category_id": category["id"],
            },
            headers=auth_headers,
        )

    response = client.get("/api/v1/posts")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


def test_get_post_by_slug(client, auth_headers):
    client.post(
        "/api/v1/posts",
        json={
            "title": "Test",
            "slug": "test",
            "content": "content",
            "status": "published",
        },
        headers=auth_headers,
    )

    response = client.get("/api/v1/posts/test")
    assert response.status_code == 200
    assert response.json()["title"] == "Test"
    # 浏览量 +1
    assert response.json()["view_count"] == 1


def test_update_post(client, auth_headers):
    create = client.post(
        "/api/v1/posts",
        json={
            "title": "Old",
            "slug": "old",
            "content": "old content",
            "status": "draft",
        },
        headers=auth_headers,
    )
    post_id = create.json()["id"]

    response = client.put(
        f"/api/v1/posts/{post_id}",
        json={"title": "New", "status": "published"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["title"] == "New"
    assert response.json()["status"] == "published"


def test_delete_post(client, auth_headers):
    create = client.post(
        "/api/v1/posts",
        json={"title": "Delete Me", "slug": "delete-me", "content": "x"},
        headers=auth_headers,
    )
    post_id = create.json()["id"]

    response = client.delete(f"/api/v1/posts/{post_id}", headers=auth_headers)
    assert response.status_code == 204

    response = client.get("/api/v1/posts/delete-me")
    assert response.status_code == 404


def test_create_post_requires_auth(client):
    response = client.post(
        "/api/v1/posts",
        json={"title": "x", "slug": "x", "content": "x"},
    )
    assert response.status_code == 401


def test_search_posts(client, auth_headers):
    client.post(
        "/api/v1/posts",
        json={
            "title": "Python Tutorial",
            "slug": "python-tutorial",
            "content": "learn python",
        },
        headers=auth_headers,
    )
    client.post(
        "/api/v1/posts",
        json={
            "title": "Java Tutorial",
            "slug": "java-tutorial",
            "content": "learn java",
        },
        headers=auth_headers,
    )

    response = client.get("/api/v1/posts?q=python")
    assert response.status_code == 200
    assert response.json()["total"] == 1
