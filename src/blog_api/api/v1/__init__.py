"""API v1。"""

from fastapi import APIRouter

from blog_api.api.v1 import auth, categories, comments, likes, posts, tags

router = APIRouter(prefix="/api/v1")
router.include_router(auth.router)
router.include_router(categories.router)
router.include_router(tags.router)
router.include_router(posts.router)
router.include_router(comments.router)
router.include_router(likes.router)

__all__ = ["router"]
