"""Post Schema。"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from blog_api.schemas.category import CategoryResponse
from blog_api.schemas.tag import TagResponse
from blog_api.schemas.user import UserResponse


class PostBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=200)
    summary: str | None = Field(None, max_length=500)
    content: str = Field(..., min_length=1)
    status: Literal["draft", "published", "archived"] = "draft"
    category_id: int | None = None
    tag_ids: list[int] = Field(default_factory=list)


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    """更新文章（所有字段可选）。"""

    title: str | None = Field(None, min_length=1, max_length=200)
    slug: str | None = Field(None, min_length=1, max_length=200)
    summary: str | None = Field(None, max_length=500)
    content: str | None = Field(None, min_length=1)
    status: Literal["draft", "published", "archived"] | None = None
    category_id: int | None = None
    tag_ids: list[int] | None = None


class PostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    slug: str
    summary: str | None
    content: str
    content_html: str | None
    status: str
    view_count: int
    category_id: int | None
    published_at: datetime | None
    created_at: datetime
    updated_at: datetime
    author: UserResponse
    category: CategoryResponse | None
    tags: list[TagResponse]


class PostListItem(BaseModel):
    """列表用的精简版。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    slug: str
    summary: str | None
    status: str
    view_count: int
    created_at: datetime
    category: CategoryResponse | None
    tags: list[TagResponse]


class PostListResponse(BaseModel):
    """分页响应。"""

    items: list[PostListItem]  # ← 关键改动
    total: int
    page: int
    size: int
    pages: int
