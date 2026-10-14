"""手动测试所有 API。"""

import httpx

BASE = "http://localhost:8000/api/v1"


def main() -> None:
    client = httpx.Client(base_url=BASE, timeout=10)

    # 1. 登录
    r = client.post(
        "/auth/login",
        data={
            "username": "sanging",
            "password": "password123",
        },
    )
    print(f"登录: {r.status_code}")
    if r.status_code != 200:
        print(f"  失败: {r.text}")
        return
    token = r.json()["access_token"]
    print(f"  token={token[:30]}...")

    headers = {"Authorization": f"Bearer {token}"}

    # 2. 当前用户
    r = client.get("/auth/me", headers=headers)
    print(f"/me: {r.status_code}")
    if r.status_code == 200:
        print(f"  user={r.json().get('username')}")

    # 3. 创建分类
    r = client.post("/categories", json={"name": "Tech", "slug": "tech"}, headers=headers)
    print(f"创建分类: {r.status_code}")
    if r.status_code == 201:
        category_id = r.json()["id"]
    else:
        r = client.get("/categories")
        category_id = r.json()[0]["id"]
    print(f"  category_id={category_id}")

    # 4. 创建标签
    r = client.post("/tags", json={"name": "Python", "slug": "python"}, headers=headers)
    print(f"创建标签: {r.status_code}")
    if r.status_code == 201:
        tag_id = r.json()["id"]
    else:
        r = client.get("/tags")
        tag_id = r.json()[0]["id"]
    print(f"  tag_id={tag_id}")

    # 5. 创建文章
    r = client.post(
        "/posts",
        json={
            "title": "FastAPI 入门",
            "slug": "fastapi-intro",
            "content": "FastAPI 是一个现代 Python Web 框架",
            "status": "published",
            "category_id": category_id,
            "tag_ids": [tag_id],
        },
        headers=headers,
    )
    print(f"创建文章: {r.status_code}")
    if r.status_code == 201:
        post = r.json()
        print(f"  post_id={post['id']}, title={post['title']}")
        print(f"  author={post['author']['username']}")
        print(f"  tags={[t['name'] for t in post['tags']]}")
    else:
        print(f"  失败: {r.text}")

    # 6. 列表
    r = client.get("/posts")
    print(f"文章列表: total={r.json()['total']}")

    client.close()


if __name__ == "__main__":
    main()
