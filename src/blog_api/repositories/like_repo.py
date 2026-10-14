"""Like 数据访问"""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from blog_api.models import Like


class LikeRepository:
    def __init__(self, session: Session):
        self.session = session

    def get(self, user_id: int, post_id: int) -> Like | None:
        stmt = select(Like).where(Like.user_id == user_id, Like.post_id == post_id)
        return self.session.execute(stmt).scalars().one_or_none()

    def create(self, user_id: int, post_id: int) -> Like:
        like = Like(user_id=user_id, post_id=post_id)
        self.session.add(like)
        self.session.flush()
        return like

    def delete(self, like: Like) -> None:
        self.session.delete(like)

    def count_by_post(self, post_id: int) -> int:
        stmt = select(func.count(Like.id)).where(Like.post_id == post_id)
        return self.session.execute(stmt).scalars().one()

    def is_liked(self, user_id: int, post_id: int) -> bool:
        return self.get(user_id, post_id) is not None
