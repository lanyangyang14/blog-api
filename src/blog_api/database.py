"""数据库连接和Session管理"""
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

from blog_api.config import settings


class Base(DeclarativeBase):
    """所有ORM模型的基类"""

    pass


# 创建引擎
engine = create_engine(
    settings.database_url,
    echo=settings.debug,  # 调试时打印SQL
    pool_pre_ping=True,  # 连接前检查
    future=True,
)

# session 工场
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,  # commit后对象不过期
)


def get_db()->Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
