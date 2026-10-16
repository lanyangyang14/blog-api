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
async def register(data: UserCreate, db: DbSession) -> User:
    """注册新用户。"""
    service = AuthService(db)
    return await service.register(data)


@router.post(
    "/login",
    response_model=Token,
    summary="登录（OAuth2 form-data）",
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DbSession,
) -> Token:
    """登录，返回 JWT。"""
    service = AuthService(db)
    _, token = await service.login(form_data.username, form_data.password)
    return Token(access_token=token)


@router.post(
    "/login/json",
    response_model=Token,
    summary="登录（JSON）",
)
async def login_json(data: UserLogin, db: DbSession) -> Token:
    """登录，返回 JWT。"""
    service = AuthService(db)
    _, token = await service.login(data.username, data.password)
    return Token(access_token=token)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="当前用户",
)
async def me(current_user: CurrentUser) -> User:
    """获取当前登录用户信息。"""
    return current_user
