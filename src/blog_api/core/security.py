"""安全相关工具：密码哈希、JWT。"""

from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from pwdlib import PasswordHash

from blog_api.config import settings
from blog_api.exceptions import UnauthorizedError

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """哈希密码。"""
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码。"""
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(
    subject: str | int,
    expires_delta: timedelta | None = None,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """创建 JWT access token。"""
    now = datetime.now(UTC)
    expire = now + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))

    payload: dict[str, Any] = {
        "sub": str(subject),
        "iat": now,
        "exp": expire,
        "type": "access",
    }
    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    """解码 JWT。"""
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        return payload
    except JWTError as e:
        raise UnauthorizedError("无效的 token") from e


def get_subject_from_token(token: str) -> str:
    """从 token 中提取 subject。"""
    payload = decode_access_token(token)
    subject = payload.get("sub")
    if not subject:
        raise UnauthorizedError("token 缺少 subject")
    return str(subject)
