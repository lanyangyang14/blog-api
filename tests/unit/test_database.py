"""测试数据库（异步）。"""

import pytest
from sqlalchemy import inspect


@pytest.mark.asyncio
async def test_engine_connects(test_engine):
    """引擎能连接。"""
    async with test_engine.connect() as conn:
        assert conn is not None


@pytest.mark.asyncio
async def test_user_tables_exist(test_engine):
    """users 表存在。"""
    async with test_engine.connect() as conn:
        tables = await conn.run_sync(lambda sync_conn: inspect(sync_conn).get_table_names())
        assert "users" in tables


@pytest.mark.asyncio
async def test_users_columns(test_engine):
    """users 表有正确的列。"""
    async with test_engine.connect() as conn:
        columns = await conn.run_sync(
            lambda sync_conn: {col["name"] for col in inspect(sync_conn).get_columns("users")}
        )
        expected = {
            "id",
            "username",
            "email",
            "hashed_password",
            "nickname",
            "avatar_url",
            "bio",
            "role",
            "is_active",
            "created_at",
            "updated_at",
        }
        assert expected.issubset(columns)
