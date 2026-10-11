"""User模型"""

from datetime import datetime

from sqlalchemy import Boolean,DateTime,String,func
from sqlalchemy.orm import Mapped,mapped_column

from blog_api.database import Base


class User(Base):
    """用户"""

    __tablename__ = "users"

    id:Mapped[int]=mapped_column(primary_key=True)
    username:Mapped[str]=mapped_column(String(50),unique=True,index=True)
    email:Mapped[str]=mapped_column(String(255),unique=True,index=True)
    hashed_password:Mapped[str]=mapped_column(String(255))
    nickname:Mapped[str|None]=mapped_column(String(50),default=None)
    avatar_url:Mapped[str|None]=mapped_column(String(500),default=None)
    bio:Mapped[str|None]=mapped_column(String(500),default=None)
    role:Mapped[str]=mapped_column(String(20),default="user")
    is_active:Mapped[bool]=mapped_column(Boolean,default=True)
    created_at:Mapped[datetime]=mapped_column(DateTime,server_default=func.now(),onupdate=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self)->str :
        return f"<User(id={self.id},username={self.username})>"
