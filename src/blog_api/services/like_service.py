"""Like 服务。"""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from blog_api.core.cache import cache
from blog_api.core.rate_limit import check_rate_limit
from blog_api.exceptions import ConflictError, NotFoundError
from blog_api.models import User
from blog_api.repositories import LikeRepository, PostRepository
from blog_api.schemas import LikeResponse

logger = logging.getLogger(__name__)


class LikeService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = LikeRepository(session)
        self.post_repo = PostRepository(session)

    async def like(self, post_id: int, user: User) -> LikeResponse:
        await check_rate_limit(f"rate:user:{user.id}:like", max_requests=10, window_seconds=60)

        if not await self.post_repo.get_by_id(post_id):
            raise NotFoundError("Post", post_id)
        if await self.repo.is_liked(user.id, post_id):
            raise ConflictError("已经点过赞")

        await self.repo.create(user.id, post_id)
        await self.session.commit()
        await cache.delete(f"post:{post_id}:like_count")

        count = await self.repo.count_by_post(post_id)
        logger.info("点赞: user_id=%s, post_id=%s", user.id, post_id)
        return LikeResponse(post_id=post_id, like_count=count, is_liked=True)

    async def unlike(self, post_id: int, user: User) -> LikeResponse:
        if not await self.post_repo.get_by_id(post_id):
            raise NotFoundError("Post", post_id)
        like = await self.repo.get(user.id, post_id)
        if not like:
            raise NotFoundError("Like", post_id)

        await self.repo.delete(like)
        await self.session.commit()
        await cache.delete(f"post:{post_id}:like_count")

        count = await self.repo.count_by_post(post_id)
        return LikeResponse(post_id=post_id, like_count=count, is_liked=False)

    async def get_status(self, post_id: int, user: User | None) -> LikeResponse:
        cache_key = f"post:{post_id}:like_count"
        count = await cache.get(cache_key)
        if count is None:
            count = await self.repo.count_by_post(post_id)
            await cache.set(cache_key, count, ttl=60)

        is_liked = await self.repo.is_liked(user.id, post_id) if user else False
        return LikeResponse(post_id=post_id, like_count=count, is_liked=is_liked)
