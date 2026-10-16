"""Tag 服务。"""

from sqlalchemy.ext.asyncio import AsyncSession

from blog_api.exceptions import ConflictError, NotFoundError
from blog_api.models import Tag
from blog_api.repositories import TagRepository
from blog_api.schemas import TagCreate


class TagService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = TagRepository(session)

    async def create(self, data: TagCreate) -> Tag:
        if await self.repo.get_by_name(data.name):
            raise ConflictError(f"标签 {data.name!r} 已存在")

        tag = Tag(**data.model_dump())
        await self.repo.create(tag)
        await self.session.commit()
        category = await self.repo.get_by_id(tag.id)
        assert category is not None
        return tag

    async def get(self, tag_id: int) -> Tag:
        tag = await self.repo.get_by_id(tag_id)
        if not tag:
            raise NotFoundError("Tag", tag_id)
        return tag

    async def list_all(self) -> list[Tag]:
        return await self.repo.list_all()

    async def delete(self, tag_id: int) -> None:
        tag = await self.get(tag_id)
        await self.repo.delete(tag)
        await self.session.commit()
