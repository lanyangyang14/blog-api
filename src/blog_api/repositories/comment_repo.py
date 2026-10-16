"""Comment 数据访问。"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from blog_api.models import Comment


class CommentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, comment: Comment) -> Comment:
        self.session.add(comment)
        await self.session.flush()
        return comment

    async def get_by_id(self, comment_id: int) -> Comment | None:
        stmt = select(Comment).where(Comment.id == comment_id).options(selectinload(Comment.author))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_post(self, post_id: int, include_deleted: bool = False) -> list[Comment]:
        stmt = (
            select(Comment)
            .where(Comment.post_id == post_id, Comment.parent_id.is_(None))
            .options(
                selectinload(Comment.author),
                # 第 1 层 replies
                selectinload(Comment.replies).selectinload(Comment.author),
                # 第 2 层 replies
                selectinload(Comment.replies)
                .selectinload(Comment.replies)
                .selectinload(Comment.author),
            )
            .order_by(Comment.created_at.desc())
        )
        if not include_deleted:
            stmt = stmt.where(Comment.is_deleted.is_(False))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete(self, comment: Comment) -> None:
        await self.session.delete(comment)
