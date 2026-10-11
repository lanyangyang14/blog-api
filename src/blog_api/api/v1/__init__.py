"""API V1"""

from fastapi import APIRouter

from blog_api.api.v1 import auth

router = APIRouter(prefix="/api/v1")
router.include_router(auth.router)

__all__ = ["router"]
