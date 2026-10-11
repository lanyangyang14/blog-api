"""user相关的 pydantic schema"""

from datetime import datetime

from pydantic import BaseModel,ConfigDict,EmailStr,Field


class UserBase(BaseModel):
    """用户基础字段"""

    username:str=Field(...,min_length=3,max_length=50)
    email: EmailStr
    nickname: str|None=Field(None,max_length=50)
    avatar_url: str|None=Field(None,max_length=500)
    bio: str|None=Field(None,max_length=500)


class UserCreate(UserBase):
    """注册请求"""

    password:str=Field(...,min_length=8,max_length=72)


class UserLogin(BaseModel):
    """登录请求"""

    username:str
    password:str
class UserUpdate(BaseModel):
    """更新用户资料（可选字段）。"""

    nickname: str | None = Field(None, max_length=50)
    avatar_url: str | None = Field(None, max_length=500)
    bio: str | None = Field(None, max_length=500)


class UserResponse(UserBase):
    """用户响应"""

    model_config=ConfigDict(from_attributes=True)

    id:int
    role:str
    is_active:bool
    created_at:datetime


class Token(BaseModel):
    """登陆响应"""

    access_token:str
    token_type:str="bearer"


class TokenPayload(BaseModel):
    """JWT payload"""

    sub:str
    exp:int
    type:str