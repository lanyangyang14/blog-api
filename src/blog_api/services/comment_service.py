"""Comment 服务。"""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from blog_api.core.metrics import comments_created_total
from blog_api.exceptions import ForbiddenError, NotFoundError, ValidationError
from blog_api.models import Comment, User
from blog_api.repositories import CommentRepository, PostRepository
from blog_api.schemas import CommentCreate, CommentUpdate

logger = logging.getLogger(__name__)


class CommentService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = CommentRepository(session)
        self.post_repo = PostRepository(session)

    async def create(self, post_id: int, data: CommentCreate, author: User) -> Comment:
        if not await self.post_repo.get_by_id(post_id):
            raise NotFoundError("Post", post_id)

        if data.parent_id:
            parent = await self.repo.get_by_id(data.parent_id)
            if not parent:
                raise NotFoundError("Comment", data.parent_id)
            if parent.post_id != post_id:
                raise ValidationError("parent_id", "父评论不属于此文章")

        comment = Comment(
            post_id=post_id,
            author_id=author.id,
            parent_id=data.parent_id,
            content=data.content,
        )
        await self.repo.create(comment)
        await self.session.commit()
        refreshed = await self.repo.get_by_id(comment.id)
        if refreshed is None:
            raise RuntimeError("Comment not found after commit")
        comments_created_total.inc()
        return refreshed

    async def get(self, comment_id: int) -> Comment:
        comment = await self.repo.get_by_id(comment_id)
        if not comment:
            raise NotFoundError("Comment", comment_id)
        return comment

    async def list_tree(self, post_id: int) -> list[Comment]:
        if not await self.post_repo.get_by_id(post_id):
            raise NotFoundError("Post", post_id)
        return await self.repo.list_by_post(post_id)

    async def update(self, comment_id: int, data: CommentUpdate, current_user: User) -> Comment:
        comment = await self.get(comment_id)
        if comment.author_id != current_user.id and current_user.role != "admin":
            raise ForbiddenError("无权修改此评论")
        comment.content = data.content
        await self.session.commit()
        refreshed = await self.repo.get_by_id(comment_id)
        if refreshed is None:
            raise RuntimeError("Comment not found after update")
        return refreshed

    async def delete(self, comment_id: int, current_user: User) -> None:
        comment = await self.get(comment_id)
        if comment.author_id != current_user.id and current_user.role != "admin":
            raise ForbiddenError("无权删除此评论")
        comment.is_deleted = True
        comment.content = "[已删除]"
        await self.session.commit()
