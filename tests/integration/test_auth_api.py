"""认证API集成测试"""


def test_register_success(client):
    """注册成功"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "alice",
            "email": "alice@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "alice"
    assert data["email"] == "alice@example.com"
    assert "hashed_password" not in data
    assert data["role"] == "user"


def test_register_duplicate_username(client):
    """用户名重复"""
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "alice",
            "email": "alice@example.com",
            "password": "password123",
        },
    )
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "alice",
            "email": "other@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 409


def test_register_duplicate_email(client):
    """邮箱重复"""
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "alice",
            "email": "alice@example.com",
            "password": "password123",
        },
    )
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "bob",
            "email": "alice@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 409


def test_register_invalid_email(client):
    """邮箱格式错误"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "alice",
            "email": "invalid",
            "password": "password123",
        },
    )
    assert response.status_code == 422


def test_register_short_password(client):
    """密码太短"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "alice",
            "email": "alice@example.com",
            "password": "short",
        },
    )
    assert response.status_code == 422


def test_login_success(client):
    """登录成功。"""
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "alice",
            "email": "alice@example.com",
            "password": "password123",
        },
    )
    response = client.post(
        "/api/v1/auth/login/json",
        json={
            "username": "alice",
            "password": "password123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    """密码错误。"""
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "alice",
            "email": "alice@example.com",
            "password": "password123",
        },
    )
    response = client.post(
        "/api/v1/auth/login/json",
        json={
            "username": "alice",
            "password": "wrong",
        },
    )
    assert response.status_code == 401


def test_login_user_not_found(client):
    """用户不存在。"""
    response = client.post(
        "/api/v1/auth/login/json",
        json={
            "username": "nobody",
            "password": "password123",
        },
    )
    assert response.status_code == 401


def test_me_success(client):
    """获取当前用户。"""
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "alice",
            "email": "alice@example.com",
            "password": "password123",
        },
    )
    login_response = client.post(
        "/api/v1/auth/login/json",
        json={
            "username": "alice",
            "password": "password123",
        },
    )
    token = login_response.json()["access_token"]

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["username"] == "alice"


def test_me_no_token(client):
    """没 token。"""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_me_invalid_token(client):
    """无效 token。"""
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid.token.here"},
    )
    assert response.status_code == 401
