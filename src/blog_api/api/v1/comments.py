"""Comment API。"""

from fastapi import APIRouter, status

from blog_api.api.deps import CurrentUser, DbSession
from blog_api.models import Comment
from blog_api.schemas import CommentCreate, CommentResponse, CommentTree, CommentUpdate
from blog_api.services import CommentService

router = APIRouter(tags=["comments"])


@router.post(
    "/posts/{post_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_comment(
    post_id: int, data: CommentCreate, db: DbSession, current_user: CurrentUser
) -> Comment:
    service = CommentService(db)
    return service.create(post_id, data, current_user)


@router.get("/posts/{post_id}/comments", response_model=list[CommentTree])
def list_comments(post_id: int, db: DbSession) -> list[Comment]:
    service = CommentService(db)
    return service.list_tree(post_id)


@router.put("/comments/{comment_id}", response_model=CommentResponse)
def update_comment(
    comment_id: int, data: CommentUpdate, db: DbSession, current_user: CurrentUser
) -> Comment:
    service = CommentService(db)
    return service.update(comment_id, data, current_user)


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(comment_id: int, db: DbSession, current_user: CurrentUser) -> None:
    service = CommentService(db)
    service.delete(comment_id, current_user)
