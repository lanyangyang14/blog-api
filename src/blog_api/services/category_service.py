"""Category 服务"""

import logging

from sqlalchemy.orm import Session

from blog_api.exceptions import ConflictError, NotFoundError
from blog_api.models import Category
from blog_api.repositories.category_repo import CategoryRepository
from blog_api.schemas import CategoryCreate, CategoryUpdate

logger = logging.getLogger(__name__)


class CategoryService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = CategoryRepository(session)

    def create(self, data: CategoryCreate) -> Category:
        if self.repo.get_by_name(data.name):
            raise ConflictError(f"Category with name {data.name} already exists!")
        if self.repo.get__by_slug(data.slug):
            raise ConflictError(f"Category with slug {data.slug} already exists!")

        category = Category(**data.model_dump())
        self.session.add(category)
        self.session.commit()
        self.session.refresh(category)
        return category

    def get(self, category_id: int) -> Category:
        category = self.repo.get_by_id(category_id)
        if not category:
            raise NotFoundError("Category", category_id)
        return category

    def list_all(self) -> list[Category]:
        return self.repo.list_all()

    def update(self, category_id: int, data: CategoryUpdate) -> Category:
        category = self.get(category_id)
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(category, key, value)
        self.session.commit()
        self.session.refresh(category)
        return category

    def delete(self, category_id: int) -> None:
        category = self.get(category_id)
        self.session.delete(category)
        self.session.commit()
