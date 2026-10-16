"""Like 数据访问。"""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from blog_api.models import Like


class LikeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, user_id: int, post_id: int) -> Like | None:
        stmt = select(Like).where(Like.user_id == user_id, Like.post_id == post_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, user_id: int, post_id: int) -> Like:
        like = Like(user_id=user_id, post_id=post_id)
        self.session.add(like)
        await self.session.flush()
        return like

    async def delete(self, like: Like) -> None:
        await self.session.delete(like)

    async def count_by_post(self, post_id: int) -> int:
        stmt = select(func.count(Like.id)).where(Like.post_id == post_id)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def is_liked(self, user_id: int, post_id: int) -> bool:
        return await self.get(user_id, post_id) is not None
