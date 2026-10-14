"""Like API。"""

from fastapi import APIRouter

from blog_api.api.deps import CurrentUser, DbSession
from blog_api.schemas import LikeResponse
from blog_api.services import LikeService

router = APIRouter(tags=["likes"])


@router.post("/posts/{post_id}/like", response_model=LikeResponse)
def like_post(post_id: int, db: DbSession, current_user: CurrentUser) -> LikeResponse:
    service = LikeService(db)
    return service.like(post_id, current_user)


@router.delete("/posts/{post_id}/like", response_model=LikeResponse)
def unlike_post(post_id: int, db: DbSession, current_user: CurrentUser) -> LikeResponse:
    service = LikeService(db)
    return service.unlike(post_id, current_user)


@router.get("/posts/{post_id}/like", response_model=LikeResponse)
def get_like_status(post_id: int, db: DbSession, current_user: CurrentUser) -> LikeResponse:
    service = LikeService(db)
    return service.get_status(post_id, current_user)
