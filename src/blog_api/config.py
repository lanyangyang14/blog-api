"""应用配置。从环境变量读取，带类型校验"""
from functools import lru_cache
from typing import Literal


from pydantic import Field,field_validator
from pydantic_settings import BaseSettings,SettingsConfigDict



class Settings(BaseSettings):
    """应用配置"""
    model_config=SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra="ignore"
    )
    #=======应用=======
    app_name:str = "blog-api"
    app_env : Literal["development", "testing", "production"]="development"
    debug: bool = False
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    log_dir:str = "logs"

    #========安全======
    secret_key:str = Field(...,min_length=32)
    access_token_expire_minutes:int = 30
    algorithm:str = "HS256"

    #=======数据库======
    database_url:str = "sqlite:///./blog.db"

    #=======CORS=======
    cors_origins:list[str]= ["http://localhost:3000","http://localhost:8000"]
    @field_validator("cors_origins",mode="before")
    @classmethod
    def parse_cors_origins(cls,v):
        """支持从逗号分割字符串解析"""
        if isinstance(v,str):
            return [origin.strip() for origin in v.split(",")if origin.strip()]
        return v
    @field_validator("log_level",mode="before")
    @classmethod
    def upper_log_level(cls,v):
        if isinstance(v,str):
            return v.upper()
        return v

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

@lru_cache(maxsize=None)
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()

#全局配置对象
settings = get_settings()





