"FastAPI应用入口"
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from blog_api.excption_handlers import register_exception_handlers
from blog_api.config import settings
from blog_api.logging_config import get_logger,setup_logging

@asynccontextmanager
async def lifespan(app:FastAPI):
    """应用生命周期"""
    #启动时
    setup_logging()
    logger = get_logger(__name__)
    logger.info("="*60)
    logger.info("%s 启动",settings.app_name)
    logger.info("环境%s" , settings.app_env)
    logger.info("调试%s",settings.debug)
    logger.info("=*60")

    yield

    #关闭时
    logger.info("%s 关闭",settings.app_name)



app=FastAPI(title="setting_app_name",
            version="0.1.0",
            description="A blog API built with FastAPI ",
            lifespan=lifespan,
            docs_url="/docs" if not settings.is_production else None,
            redoc_url="/redoc" if not settings.is_production else None,
             )

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],

)

#注册异常处理器
register_exception_handlers(app)


@app.get("/",tags=["root"])
def root()->dict[str,str]:
    return {
        "name":settings.app_name,
        "version":"0.1.0",
        "env":settings.app_env,
        "docs":"/docs",
    }


@app.get("/health")
def health()->dict[str,str]:
    """健康检测"""
    return {"status":"ok"}