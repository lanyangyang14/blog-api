"""Category 数据访问。"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from blog_api.models import Category


class CategoryRepository:
    """Category 的数据库操作（异步）。"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, category: Category) -> Category:
        """创建分类（flush，不 commit）。"""
        self.session.add(category)
        await self.session.flush()
        return category

    async def get_by_id(self, category_id: int) -> Category | None:
        """按 ID 查。"""
        return await self.session.get(Category, category_id)

    async def get_by_name(self, name: str) -> Category | None:
        """按名称查。"""
        stmt = select(Category).where(Category.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Category | None:
        """按 slug 查。"""
        stmt = select(Category).where(Category.slug == slug)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(self) -> list[Category]:
        """列出所有分类。"""
        stmt = select(Category).order_by(Category.name)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def exists_name(self, name: str) -> bool:
        """名称是否存在。"""
        return await self.get_by_name(name) is not None

    async def exists_slug(self, slug: str) -> bool:
        """slug 是否存在。"""
        return await self.get_by_slug(slug) is not None

    async def delete(self, category: Category) -> None:
        """删除分类。"""
        await self.session.delete(category)
