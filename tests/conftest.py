"""pytest 全局配置。"""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import Session, sessionmaker

import blog_api.models  # noqa: F401  确保模型已注册
from blog_api.database import Base, get_db
from blog_api.main import app


@pytest.fixture(scope="session")
def test_engine():
    """测试用的内存数据库。"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # ← 关键：让所有连接共享同一个内存数据库
    )
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture()
def db_session(test_engine) -> Generator[Session]:
    """每个测试独立事务，结束后回滚。"""
    connection = test_engine.connect()
    transaction = connection.begin()
    session_local = sessionmaker(bind=connection)  # ← 绑 connection
    session = session_local()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db_session) -> Generator[TestClient]:
    """测试客户端，用测试数据库。"""

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def sample_user_data():
    """ "通用用户数据"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123",
    }


@pytest.fixture()
def register_user(client, sample_user_data):
    """注册并返回用户信息的fixture"""
    response = client.post("/api/v1/auth/register", json=sample_user_data)
    assert response.status_code == 201
    return response.json()


@pytest.fixture()
def auth_token(client, sample_user_data):
    """登陆并返回token的fixture"""
    client.post("/api/v1/auth/login", json=sample_user_data)
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": sample_user_data["username"],
            "password": sample_user_data["password"],
        },
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture()
def auth_headers(auth_token):
    """带token的headers"""
    return {"Authorization": f"Bearer {auth_token}"}
