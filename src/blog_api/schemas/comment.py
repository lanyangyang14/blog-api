"""Comment Schema。"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from blog_api.schemas.user import UserResponse


class CommentCreate(BaseModel):
    """创建评论。"""

    content: str = Field(..., min_length=1, max_length=2000)
    parent_id: int | None = None


class CommentUpdate(BaseModel):
    """更新评论。"""

    content: str = Field(..., min_length=1, max_length=2000)


class CommentResponse(BaseModel):
    """评论响应。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    post_id: int
    parent_id: int | None  # ← 关键
    content: str
    is_deleted: bool
    created_at: datetime
    author: UserResponse


class CommentTree(CommentResponse):
    """带嵌套回复的评论。"""

    replies: list["CommentTree"] = Field(default_factory=list)


CommentTree.model_rebuild()
