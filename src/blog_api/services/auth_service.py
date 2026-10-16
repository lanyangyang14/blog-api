"""认证服务。"""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from blog_api.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from blog_api.exceptions import ConflictError, UnauthorizedError
from blog_api.logging_config import get_trace_id
from blog_api.models import User
from blog_api.repositories import UserRepository
from blog_api.schemas import UserCreate

logger = logging.getLogger(__name__)


class AuthService:
    """注册、登录。"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = UserRepository(session)

    async def register(self, data: UserCreate) -> User:
        """注册用户。"""
        if await self.repo.exists_username(data.username):
            raise ConflictError(f"用户名 {data.username!r} 已被注册")
        if await self.repo.exists_email(data.email):
            raise ConflictError(f"邮箱 {data.email!r} 已被注册")

        user = User(
            username=data.username,
            email=data.email,
            hashed_password=hash_password(data.password),
            nickname=data.nickname,
            avatar_url=data.avatar_url,
            bio=data.bio,
        )

        try:
            await self.repo.create(user)
            await self.session.commit()
            await self.session.refresh(user)
        except Exception:
            await self.session.rollback()
            logger.exception("注册失败: username=%s", data.username)
            raise

        # 异步发送邮件（不阻塞注册）
        from blog_api.tasks.email import send_welcome_email

        send_welcome_email.delay(
            user_id=user.id,
            email=user.email,
            username=user.username,
            trace_id=get_trace_id(),
        )
        logger.info("用户注册成功: id=%s, username=%s", user.id, user.username)
        return user

    async def authenticate(self, username: str, password: str) -> User:
        """验证用户名密码。"""
        user = await self.repo.get_by_username(username)
        if not user or not verify_password(password, user.hashed_password):
            logger.warning("登录失败: username=%s", username)
            raise UnauthorizedError("用户名或密码错误")
        if not user.is_active:
            raise UnauthorizedError("账号已被禁用")
        return user

    async def login(self, username: str, password: str) -> tuple[User, str]:
        """登录，返回 (user, token)。"""
        user = await self.authenticate(username, password)
        token = create_access_token(
            subject=user.id,
            extra_claims={"username": user.username, "role": user.role},
        )
        logger.info("用户登录成功: id=%s", user.id)
        return user, token

    async def get_by_id(self, user_id: int) -> User | None:
        return await self.repo.get_by_id(user_id)
