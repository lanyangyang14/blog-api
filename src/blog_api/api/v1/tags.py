"""Tag API。"""

from fastapi import APIRouter, status

from blog_api.api.deps import DbSession
from blog_api.models import Tag
from blog_api.schemas import TagCreate, TagResponse
from blog_api.services import TagService

router = APIRouter(prefix="/tags", tags=["tags"])


@router.post("", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(data: TagCreate, db: DbSession) -> Tag:
    service = TagService(db)
    return await service.create(data)


@router.get("", response_model=list[TagResponse])
async def list_tags(db: DbSession) -> list[Tag]:
    service = TagService(db)
    return await service.list_all()


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(tag_id: int, db: DbSession) -> None:
    service = TagService(db)
    await service.delete(tag_id)
