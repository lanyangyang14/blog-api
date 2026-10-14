"""认证 API。"""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from blog_api.api.deps import CurrentUser, DbSession
from blog_api.models import User
from blog_api.schemas import Token, UserCreate, UserLogin, UserResponse
from blog_api.services import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="注册",
)
def register(data: UserCreate, db: DbSession) -> User:
    """注册新用户。"""
    service = AuthService(db)
    return service.register(data)


@router.post(
    "/login",
    response_model=Token,
    summary="登录（OAuth2 form-data）",
)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DbSession,
) -> Token:
    """登录，返回 JWT。Swagger Authorize 用这个。"""
    service = AuthService(db)
    _, token = service.login(form_data.username, form_data.password)
    return Token(access_token=token)


@router.post(
    "/login/json",
    response_model=Token,
    summary="登录（JSON）",
)
def login_json(data: UserLogin, db: DbSession) -> Token:
    """登录，返回 JWT。前端/脚本用这个。"""
    service = AuthService(db)
    _, token = service.login(data.username, data.password)
    return Token(access_token=token)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="当前用户",
)
def me(current_user: CurrentUser) -> User:
    """获取当前登录用户信息。"""
    return current_user
