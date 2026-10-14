"""数据访问"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from blog_api.models import Tag


class TagRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, tag: Tag) -> Tag:
        self.session.add(tag)
        self.session.flush()
        return tag

    def get_by_id(self, tag_id: int) -> Tag | None:
        return self.session.get(Tag, tag_id)

    def get_by_name(self, name: str) -> Tag | None:
        stmt = select(Tag).where(Tag.name == name)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_or_create(self, name: str, slug: str) -> Tag:
        """存在就返回，不存在就创建。"""
        tag = self.get_by_name(name)
        if tag:
            return tag
        tag = Tag(name=name, slug=slug)
        return self.create(tag)

    def list_all(self) -> list[Tag]:
        stmt = select(Tag).order_by(Tag.name)
        return list(self.session.execute(stmt).scalars().all())

    def delete(self, tag: Tag) -> None:
        self.session.delete(tag)
