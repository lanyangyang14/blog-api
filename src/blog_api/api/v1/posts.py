"""Post API。"""

from typing import Literal

from fastapi import APIRouter, Query, status

from blog_api.api.deps import CurrentUser, DbSession
from blog_api.models import Post
from blog_api.schemas import (
    PostCreate,
    PostListItem,
    PostListResponse,
    PostResponse,
    PostUpdate,
)
from blog_api.services import PostService

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(data: PostCreate, db: DbSession, current_user: CurrentUser) -> Post:
    service = PostService(db)
    return await service.create(data, current_user)


@router.get("", response_model=PostListResponse)
async def list_posts(
    db: DbSession,
    page: int = Query(1, ge=1, le=1000),
    size: int = Query(20, ge=1, le=100),
    status_filter: Literal["draft", "published", "archived"] | None = Query(None, alias="status"),
    category_id: int | None = None,
    author_id: int | None = None,
    tag_id: int | None = None,
    q: str | None = None,
    sort: str = Query("-created_at"),
) -> PostListResponse:
    service = PostService(db)
    posts, total = await service.list_posts(
        page=page,
        size=size,
        status=status_filter,
        category_id=category_id,
        author_id=author_id,
        tag_id=tag_id,
        q=q,
        sort=sort,
    )
    pages = (total + size - 1) // size
    return PostListResponse(
        items=[PostListItem.model_validate(p) for p in posts],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@router.get("/{slug}", response_model=PostResponse)
async def get_post(slug: str, db: DbSession) -> Post:
    service = PostService(db)
    return await service.get_by_slug(slug)


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int, data: PostUpdate, db: DbSession, current_user: CurrentUser
) -> Post:
    service = PostService(db)
    return await service.update(post_id, data, current_user)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, db: DbSession, current_user: CurrentUser) -> None:
    service = PostService(db)
    await service.delete(post_id, current_user)
