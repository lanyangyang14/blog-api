"""Like服务"""

import logging

from sqlalchemy.orm import Session

from blog_api.core.cache import cache
from blog_api.core.rate_limit import check_rate_limit
from blog_api.exceptions import ConflictError, NotFoundError
from blog_api.models import User
from blog_api.repositories import LikeRepository, PostRepository
from blog_api.schemas import LikeResponse

logger = logging.getLogger(__name__)


class LikeService:
    def __init__(self, session: Session) -> None:
        self.session = Session()
        self.repo = LikeRepository(session)
        self.post_repo = PostRepository(session)

    def like(self, post_id: int, user: User) -> LikeResponse:
        """点赞。"""
        check_rate_limit(f"rate:user:{user.id}:like", max_requests=10, window_seconds=60)
        if not self.post_repo.get_by_id(post_id):
            raise NotFoundError("Post", post_id)
        if self.repo.is_liked(user.id, post_id):
            raise ConflictError("已经点过赞")

        self.repo.create(user.id, post_id)
        self.session.commit()
        cache.delete(f"post:{post_id}:like_count")  # ← 删缓存
        count = self.repo.count_by_post(post_id)
        logger.info("点赞: user_id=%s, post_id=%s", user.id, post_id)
        return LikeResponse(post_id=post_id, like_count=count, is_like=True)

    def unlike(self, post_id: int, user: User) -> LikeResponse:
        """取消点赞。"""
        if not self.post_repo.get_by_id(post_id):
            raise NotFoundError("Post", post_id)
        like = self.repo.get(user.id, post_id)
        if not like:
            raise NotFoundError("Like", post_id)

        self.repo.delete(like)
        self.session.commit()
        count = self.repo.count_by_post(post_id)
        return LikeResponse(post_id=post_id, like_count=count, is_like=False)

    def get_status(self, post_id: int, user: User | None) -> LikeResponse:
        count = self.repo.count_by_post(post_id)
        is_liked = self.repo.is_liked(user.id, post_id) if user else False
        return LikeResponse(post_id=post_id, like_count=count, is_like=is_liked)
