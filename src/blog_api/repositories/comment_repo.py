"""Comment 数据访问"""

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from blog_api.models import Comment


class CommentRepository:
    def __init__(self, session: Session):
        self.session: Session = session

    def create(self, comment: Comment) -> Comment:
        self.session.add(comment)
        self.session.flush()
        return comment

    def get_by_id(self, comment_id: int) -> Comment | None:
        stmt = select(Comment).where(Comment.id == comment_id).options(selectinload(Comment.author))
        return self.session.execute(stmt).scalar_one_or_none()

    def list_by_post(self, post_id: int, include_deleted: bool = False) -> list[Comment]:
        """查文章下的所有评论（不含回复），回复通过parent关系加载"""
        stmt = (
            select(Comment)
            .where(Comment.post_id == post_id, Comment.parent_id.is_(None))
            .options(
                selectinload(Comment.author),
                selectinload(Comment.replies).selectinload(Comment.author),
            )
            .order_by(Comment.created_at.desc())
        )
        if not include_deleted:
            stmt = stmt.where(Comment.is_deleted.is_(False))
        return list(self.session.execute(stmt).scalars().all())

    def delete(self, comment: Comment) -> None:
        self.session.delete(comment)
