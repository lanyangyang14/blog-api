"""FastAPI 依赖。"""

from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from blog_api.core.security import decode_access_token
from blog_api.database import get_db
from blog_api.exceptions import UnauthorizedError
from blog_api.models import User
from blog_api.repositories import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

DbSession = Annotated[AsyncSession, Depends(get_db)]
TokenStr = Annotated[str, Depends(oauth2_scheme)]


async def get_current_user(db: DbSession, token: TokenStr) -> User:
    """从 token 获取当前用户。"""
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedError("token 无效")

    repo = UserRepository(db)
    user = await repo.get_by_id(int(user_id))
    if not user:
        raise UnauthorizedError("用户不存在")
    if not user.is_active:
        raise UnauthorizedError("账号已被禁用")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
