"""Tag 数据访问。"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from blog_api.models import Tag


class TagRepository:
    """Tag 的数据库操作（异步）。"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, tag: Tag) -> Tag:
        """创建标签（flush，不 commit）。"""
        self.session.add(tag)
        await self.session.flush()
        return tag

    async def get_by_id(self, tag_id: int) -> Tag | None:
        """按 ID 查。"""
        return await self.session.get(Tag, tag_id)

    async def get_by_name(self, name: str) -> Tag | None:
        """按名称查。"""
        stmt = select(Tag).where(Tag.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Tag | None:
        """按 slug 查。"""
        stmt = select(Tag).where(Tag.slug == slug)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_or_create(self, name: str, slug: str) -> Tag:
        """存在就返回，不存在就创建。"""
        tag = await self.get_by_name(name)
        if tag:
            return tag
        tag = Tag(name=name, slug=slug)
        return await self.create(tag)

    async def get_many_by_ids(self, tag_ids: list[int]) -> list[Tag]:
        """按 ID 列表批量查（用于创建文章时校验标签）。"""
        if not tag_ids:
            return []
        stmt = select(Tag).where(Tag.id.in_(tag_ids))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_all(self) -> list[Tag]:
        """列出所有标签。"""
        stmt = select(Tag).order_by(Tag.name)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def exists_name(self, name: str) -> bool:
        """名称是否存在。"""
        return await self.get_by_name(name) is not None

    async def delete(self, tag: Tag) -> None:
        """删除标签。"""
        await self.session.delete(tag)
