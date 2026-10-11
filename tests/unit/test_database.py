"""测试数据库"""

from sqlalchemy import inspect, exc

from blog_api.database import engine


def test_engine_connects():
      """引擎连接"""
      with engine.connect() as conn:
          assert conn is not None

def test_user_tables_exist():
    """表存在"""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    assert "users" in tables

def test_users_columns():
    """users表有正确的列"""
    inspector = inspect(engine)
    columns={col["name"]for col in inspector.get_columns(table_name="users")}
    expected={
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