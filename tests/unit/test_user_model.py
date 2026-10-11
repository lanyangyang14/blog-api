"""测试User模型"""

from blog_api.models import User


def test_user_create():
    """能创建User"""
    user=User(
        username="alice",
        email="alice@example.com",
        hashed_password="fake_hash",

    )
    assert user.username == "alice"
    assert user.email == "alice@example.com"

    assert user.role is None
    assert user.is_active is None


def test_user_repr():
    """repr可读"""
    user=User(
        id=1,
        username="alice",
        email="a@example.com",
        hashed_password="x",


    )
    assert "alice" in repr(user)