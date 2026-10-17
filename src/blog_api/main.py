"""FastAPI 应用入口。"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from prometheus_fastapi_instrumentator import Instrumentator

from blog_api.api import v1_router
from blog_api.config import settings
from blog_api.core.middleware import TraceIdMiddleware
from blog_api.exception_handlers import register_exception_handlers
from blog_api.logging_config import get_logger, setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """应用生命周期。"""
    setup_logging()
    logger = get_logger(__name__)
    logger.info("=" * 60)
    logger.info("%s 启动", settings.app_name)
    logger.info("环境: %s", settings.app_env)
    logger.info("调试: %s", settings.debug)
    logger.info("=" * 60)

    yield

    logger.info("%s 关闭", settings.app_name)


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="A blog API built with FastAPI",
    lifespan=lifespan,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
)

# 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(TraceIdMiddleware)

# 异常处理器
register_exception_handlers(app)

# 路由
app.include_router(v1_router)


@app.get("/", tags=["root"])
def root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "version": "0.1.0",
        "env": settings.app_env,
        "docs": "/docs",
    }


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    """健康检测。"""
    return {"status": "ok"}


Instrumentator(
    should_group_status_codes=False,
    should_ignore_untemplated=True,
    should_instrument_requests_inprogress=True,
    excluded_handlers=["/metrics", "/health"],
    inprogress_name="http_requests_inprogress",
    inprogress_labels=True,
).instrument(app)


# 手动暴露 /metrics
@app.get("/metrics", include_in_schema=False)
def metrics_endpoint() -> Response:
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )
