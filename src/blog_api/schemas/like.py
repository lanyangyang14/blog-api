"""like Schema"""

from pydantic import BaseModel


class LikeResponse(BaseModel):
    """点赞响应"""

    post_id: int
    like_count: int
    is_like: bool
