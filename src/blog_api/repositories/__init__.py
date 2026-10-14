"""数据访问层。"""

from blog_api.repositories.category_repo import CategoryRepository
from blog_api.repositories.comment_repo import CommentRepository
from blog_api.repositories.like_repo import LikeRepository
from blog_api.repositories.post_repo import PostRepository
from blog_api.repositories.tag_repo import TagRepository
from blog_api.repositories.user_repo import UserRepository

__all__ = [
    "CategoryRepository",
    "CommentRepository",
    "LikeRepository",
    "PostRepository",
    "TagRepository",
    "UserRepository",
]
