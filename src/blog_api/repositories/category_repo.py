"""Category 数据访问"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from blog_api.models import Category


class CategoryRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, category: Category) -> Category:
        self.session.add(category)
        self.session.flush()
        return category

    def get_by_id(self, category_id: int) -> Category | None:
        return self.session.get(Category, category_id)

    def get_by_name(self, name: str) -> Category | None:
        stmt = select(Category).where(Category.name == name)
        return self.session.execute(stmt).scalar_one_or_none()

    def get__by_slug(self, slug: str) -> Category | None:
        stmt = select(Category).where(Category.slug == slug)
        return self.session.execute(stmt).scalar_one_or_none()

    def list_all(self) -> list[Category]:
        stmt = select(Category).order_by(Category.name)
        return list(self.session.execute(stmt).scalars().all())

    def delete(self, category: Category) -> None:
        self.session.delete(category)
