"""认证api"""

from fastapi import APIRouter, status

from blog_api.api.deps import CurrentUser, DbSession
from blog_api.schemas import Token, UserCreate, UserLogin, UserResponse
from blog_api.services import AuthService


router=APIRouter(prefix="/auth",tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="注册"

)

def register(data:UserCreate,db:DbSession) -> UserResponse:
    """注册新用户"""
    service=AuthService(db)
    user=service.register(data)
    return user

@router.post(
    "/login",
    response_model=Token,
    summary="登录",

)
def login(data:UserLogin,db:DbSession) ->Token :
    """登录，返回JWT"""
    service=AuthService(db)
    user,token=service.login(data.username,data.password)
    return Token(access_token=token)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="当前用户",
)
def me(current_user:CurrentUser)->UserResponse:
    """"获得当前的登录用户信息"""
    return current_user
