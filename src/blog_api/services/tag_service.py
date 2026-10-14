"""Tag服务"""

from sqlalchemy.orm import Session

from blog_api.exceptions import ConflictError, NotFoundError
from blog_api.models import Tag
from blog_api.repositories import TagRepository
from blog_api.schemas import TagCreate


class TagService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = TagRepository(session)

    def create(self, data: TagCreate) -> Tag:
        if self.repo.get_by_name(data.name):
            raise ConflictError(f"标签 {data.name!r} 已存在")

        tag = Tag(**data.model_dump())
        self.repo.create(tag)
        self.session.commit()
        self.session.refresh(tag)
        return tag

    def get(self, tag_id: int) -> Tag:
        tag = self.repo.get_by_id(tag_id)
        if not tag:
            raise NotFoundError("Tag", tag_id)
        return tag

    def list_all(self) -> list[Tag]:
        return self.repo.list_all()

    def delete(self, tag_id: int) -> None:
        tag = self.get(tag_id)
        self.repo.delete(tag)
        self.session.commit()
