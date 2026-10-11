"""测试 security 模块。"""

from datetime import timedelta

import pytest

from blog_api.core.security import (
    create_access_token,
    decode_access_token,
    get_subject_from_token,
    hash_password,
    verify_password,
)
from blog_api.exceptions import UnauthorizedError

# ============ 密码哈希 ============


def test_hash_password():
    """哈希后不是明文。"""
    hashed = hash_password("mysecret")
    assert hashed != "mysecret"
    assert len(hashed) > 20


def test_hash_password_different_each_time():
    """同一密码每次哈希不同（因为 salt）。"""
    h1 = hash_password("mysecret")
    h2 = hash_password("mysecret")
    assert h1 != h2


def test_verify_password_correct():
    """正确密码能验证。"""
    hashed = hash_password("mysecret")
    assert verify_password("mysecret", hashed) is True


def test_verify_password_wrong():
    """错误密码不能验证。"""
    hashed = hash_password("mysecret")
    assert verify_password("wrong", hashed) is False


# ============ JWT ============


def test_create_access_token():
    """能创建 token。"""
    token = create_access_token(subject=1)
    assert isinstance(token, str)
    assert len(token) > 50
    assert token.count(".") == 2  # JWT 有三段


def test_decode_token():
    """能解码自己创建的 token。"""
    token = create_access_token(subject=42)
    payload = decode_access_token(token)
    assert payload["sub"] == "42"
    assert payload["type"] == "access"
    assert "exp" in payload
    assert "iat" in payload


def test_decode_token_with_extra_claims():
    """额外声明能带进去。"""
    token = create_access_token(subject=1, extra_claims={"role": "admin"})
    payload = decode_access_token(token)
    assert payload["role"] == "admin"


def test_decode_invalid_token():
    """无效 token 报错。"""
    with pytest.raises(UnauthorizedError):
        decode_access_token("invalid.token.here")


def test_decode_token_wrong_signature():
    """签名不对报错。"""
    from jose import jwt

    fake = jwt.encode({"sub": "1"}, "wrong-secret", algorithm="HS256")
    with pytest.raises(UnauthorizedError):
        decode_access_token(fake)


def test_expired_token():
    """过期 token 报错。"""
    token = create_access_token(subject=1, expires_delta=timedelta(seconds=-1))
    with pytest.raises(UnauthorizedError):
        decode_access_token(token)


def test_get_subject_from_token():
    """从 token 拿 subject。"""
    token = create_access_token(subject=123)
    assert get_subject_from_token(token) == "123"
