"""Comment 服务"""

import logging

from sqlalchemy.orm import Session

from blog_api.core.rate_limit import check_rate_limit
from blog_api.exceptions import ForbiddenError, NotFoundError, ValidationError
from blog_api.models import Comment, User
from blog_api.repositories import CommentRepository, PostRepository
from blog_api.schemas import CommentCreate, CommentUpdate

logger = logging.getLogger(__name__)


class CommentService:
    def __init__(self, session: Session):
        self.session: Session = session
        self.repo = CommentRepository(session)
        self.post_repo = PostRepository(session)

    def create(
        self,
        post_id: int,
        data: CommentCreate,
        author: User,
    ) -> Comment:
        check_rate_limit(f"rate.user:{author.id}:comment", max_requests=5, window_seconds=60)
        """创建评论"""
        if not self.post_repo.get_by_id(post_id):
            raise NotFoundError("Post", post_id)
        # 如果有parent_id，检验父评论存在且属于同一篇文章
        if data.parent_id:
            parent = self.repo.get_by_id(data.parent_id)
            if not parent:
                raise NotFoundError("Comment", data.parent_id)
            if parent.post_id != post_id:
                raise ValidationError("parent_id", "父评评论不属于此文章")
        comment = Comment(
            post_id=post_id,
            author_id=author.id,
            parent_id=data.parent_id,
            content=data.content,
        )
        self.repo.create(comment)
        self.session.commit()
        self.session.refresh(comment)
        logger.info("评论创建:id=%s,post_id=%s", comment.id, post_id)
        return comment

    def get(self, comment_id: int) -> Comment:
        comment = self.repo.get_by_id(comment_id)
        if not comment:
            raise NotFoundError("Comment", comment_id)
        return comment

    def list_tree(self, post_id: int) -> list[Comment]:
        """返回嵌套树。"""
        if not self.post_repo.get_by_id(post_id):
            raise NotFoundError("Post", post_id)
        return self.repo.list_by_post(post_id)

    def update(self, comment_id: int, data: CommentUpdate, current_user: User) -> Comment:
        comment = self.get(comment_id)
        if comment.author_id != current_user.id and current_user.role != "admin":
            raise ForbiddenError("无权修复此评论")
        comment.content = data.content
        self.session.commit()
        self.session.refresh(comment)
        return comment

    def delete(self, comment_id: int, current_user: User) -> None:
        comment = self.get(comment_id)
        if comment.author_id != current_user.id and current_user.role != "admin":
            raise ForbiddenError("无权删除此评论")
        # 软删除
        comment.is_deleted = True
        comment.content = "[已删除]"
        self.session.commit()
