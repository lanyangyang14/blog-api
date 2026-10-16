"""pytest 全局配置（异步）。"""

from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

import blog_api.models  # noqa: F401
from blog_api.database import Base, get_db
from blog_api.main import app

# ============ Mock Cache ============


@pytest_asyncio.fixture(autouse=True)
async def mock_cache(mocker):
    """Mock 缓存，测试时不连 Redis。"""
    mock = mocker.patch("blog_api.core.cache.cache")
    mock.get.return_value = None
    mock.set.return_value = None
    mock.delete.return_value = None
    mock.delete_pattern.return_value = None
    mock.incr.return_value = 1
    mock.expire.return_value = None
    return mock


# ============ 数据库 ============


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession]:
    """每个测试独立事务，结束后回滚。"""
    async with test_engine.connect() as connection:
        transaction = await connection.begin()
        session_factory = async_sessionmaker(
            bind=connection,
            expire_on_commit=False,  # ← 加这个
        )
        session = session_factory()
        try:
            yield session
        finally:
            await session.close()
            await transaction.rollback()


@pytest_asyncio.fixture
async def client(db_session) -> AsyncGenerator[AsyncClient]:
    """测试客户端。"""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


# ============ 用户 ============


@pytest_asyncio.fixture
async def sample_user_data():
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123",
    }


@pytest_asyncio.fixture
async def auth_token(client, sample_user_data):
    """注册并登录，返回 token。"""
    register_response = await client.post("/api/v1/auth/register", json=sample_user_data)
    assert register_response.status_code == 201, register_response.text

    login_response = await client.post(
        "/api/v1/auth/login/json",
        json={
            "username": sample_user_data["username"],
            "password": sample_user_data["password"],
        },
    )
    assert login_response.status_code == 200, login_response.text
    return login_response.json()["access_token"]


@pytest_asyncio.fixture
async def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}
