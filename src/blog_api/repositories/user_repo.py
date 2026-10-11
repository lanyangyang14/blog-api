"""User 数据访问。"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from blog_api.models import User


class UserRepository:
    """User 的数据库操作。"""

    def __init__(self, session: Session):
        self.session = session

    def create(self, user: User) -> User:
        """创建用户（flush，不 commit）。"""
        self.session.add(user)
        self.session.flush()
        return user

    def get_by_id(self, user_id: int) -> User | None:
        """按 ID 查。"""
        return self.session.get(User, user_id)

    def get_by_username(self, username: str) -> User | None:
        """按用户名查。"""
        stmt = select(User).where(User.username == username)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_by_email(self, email: str) -> User | None:
        """按邮箱查。"""
        stmt = select(User).where(User.email == email)
        return self.session.execute(stmt).scalar_one_or_none()

    def exists_username(self, username: str) -> bool:
        """用户名是否存在。"""
        return self.get_by_username(username) is not None

    def exists_email(self, email: str) -> bool:
        """邮箱是否存在。"""
        return self.get_by_email(email) is not None

    def update(self, user: User) -> User:
        """更新（对象已被 session 追踪，直接 flush）。"""
        self.session.flush()
        return user