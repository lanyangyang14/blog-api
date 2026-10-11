"""pytest 全局配置。"""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import Session, sessionmaker

from blog_api.database import Base, get_db
from blog_api.main import app
import blog_api.models  # noqa: F401  确保模型已注册


@pytest.fixture(scope="session")
def test_engine():
    """测试用的内存数据库。"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,   # ← 关键：让所有连接共享同一个内存数据库
    )
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture()
def db_session(test_engine) -> Generator[Session, None, None]:
    """每个测试独立事务，结束后回滚。"""
    connection = test_engine.connect()
    transaction = connection.begin()
    SessionLocal = sessionmaker(bind=connection)   # ← 绑 connection
    session = SessionLocal()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db_session) -> Generator[TestClient, None, None]:
    """测试客户端，用测试数据库。"""

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()