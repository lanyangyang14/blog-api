"""Category 服务。"""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from blog_api.exceptions import ConflictError, NotFoundError
from blog_api.models import Category
from blog_api.repositories import CategoryRepository
from blog_api.schemas import CategoryCreate, CategoryUpdate

logger = logging.getLogger(__name__)


class CategoryService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = CategoryRepository(session)

    async def create(self, data: CategoryCreate) -> Category:
        if await self.repo.get_by_name(data.name):
            raise ConflictError(f"分类 {data.name!r} 已存在")
        if await self.repo.get_by_slug(data.slug):
            raise ConflictError(f"slug {data.slug!r} 已存在")

        category = Category(**data.model_dump())
        await self.repo.create(category)
        await self.session.commit()
        refreshed = await self.repo.get_by_id(category.id)
        if refreshed is None:
            raise RuntimeError("Category not found after commit")
        return refreshed

    async def get(self, category_id: int) -> Category:
        category = await self.repo.get_by_id(category_id)
        if not category:
            raise NotFoundError("Category", category_id)
        return category

    async def list_all(self) -> list[Category]:
        return await self.repo.list_all()

    async def update(self, category_id: int, data: CategoryUpdate) -> Category:
        category = await self.get(category_id)
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(category, key, value)
        await self.session.commit()
        refreshed = await self.repo.get_by_id(category_id)
        if refreshed is None:
            raise RuntimeError("Category not found after update")
        return refreshed

    async def delete(self, category_id: int) -> None:
        category = await self.get(category_id)
        await self.repo.delete(category)
        await self.session.commit()
