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
def create_post(data: PostCreate, db: DbSession, current_user: CurrentUser) -> Post:
    """创建文章。"""
    service = PostService(db)
    return service.create(data, current_user)


@router.get("", response_model=PostListResponse)
def list_posts(
    db: DbSession,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status_filter: Literal["draft", "published", "archived"] | None = Query(None, alias="status"),
    category_id: int | None = None,
    author_id: int | None = None,
    tag_id: int | None = None,
    q: str | None = None,
    sort: str = Query("-created_at"),
) -> PostListResponse:
    """文章列表。"""
    service = PostService(db)
    posts, total = service.list_posts(
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
def get_post(slug: str, db: DbSession) -> Post:
    """文章详情（按 slug）。"""
    service = PostService(db)
    return service.get_by_slug(slug)


@router.put("/{post_id}", response_model=PostResponse)
def update_post(post_id: int, data: PostUpdate, db: DbSession, current_user: CurrentUser) -> Post:
    """更新文章。"""
    service = PostService(db)
    return service.update(post_id, data, current_user)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: DbSession, current_user: CurrentUser) -> None:
    """删除文章。"""
    service = PostService(db)
    service.delete(post_id, current_user)
