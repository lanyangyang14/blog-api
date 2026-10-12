"""测试数据库。"""

from sqlalchemy import inspect


def test_engine_connects(test_engine):
    """引擎能连接。"""
    with test_engine.connect() as conn:
        assert conn is not None


def test_user_tables_exist(test_engine):
    """users 表存在。"""
    inspector = inspect(test_engine)
    tables = inspector.get_table_names()
    assert "users" in tables


def test_users_columns(test_engine):
    """users 表有正确的列。"""
    inspector = inspect(test_engine)
    columns = {col["name"] for col in inspector.get_columns("users")}
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
