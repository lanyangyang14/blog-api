"""认证服务。"""

import logging

from sqlalchemy.orm import Session

from blog_api.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from blog_api.exceptions import ConflictError, UnauthorizedError
from blog_api.models import User
from blog_api.repositories import UserRepository
from blog_api.schemas import UserCreate

logger = logging.getLogger(__name__)


class AuthService:
    """注册、登录。"""

    def __init__(self, session: Session):
        self.session = session
        self.repo = UserRepository(session)

    def register(self, data: UserCreate) -> User:
        """注册用户。"""
        # 1. 检查冲突
        if self.repo.exists_username(data.username):
            raise ConflictError(f"用户名 {data.username!r} 已被注册")
        if self.repo.exists_email(data.email):
            raise ConflictError(f"邮箱 {data.email!r} 已被注册")

        # 2. 创建
        user = User(
            username=data.username,
            email=data.email,
            hashed_password=hash_password(data.password),
            nickname=data.nickname,
            avatar_url=data.avatar_url,
            bio=data.bio,
        )

        # 3. 保存
        try:
            self.repo.create(user)
            self.session.commit()
            self.session.refresh(user)
        except Exception:
            self.session.rollback()
            logger.exception("注册失败: username=%s", data.username)
            raise

        logger.info("用户注册成功: id=%s, username=%s", user.id, user.username)
        return user

    def authenticate(self, username: str, password: str) -> User:
        """验证用户名密码，返回 User。

        Raises:
            UnauthorizedError: 用户名或密码错误。
        """
        user = self.repo.get_by_username(username)
        if not user or not verify_password(password, user.hashed_password):
            logger.warning("登录失败: username=%s", username)
            raise UnauthorizedError("用户名或密码错误")
        if not user.is_active:
            raise UnauthorizedError("账号已被禁用")
        return user

    def login(self, username: str, password: str) -> tuple[User, str]:
        """登录，返回 (user, token)。"""
        user = self.authenticate(username, password)
        token = create_access_token(
            subject=user.id,
            extra_claims={"username": user.username, "role": user.role},
        )
        logger.info("用户登录成功: id=%s", user.id)
        return user, token

    def get_by_id(self, user_id: int) -> User | None:
        return self.repo.get_by_id(user_id)