"""全局异常处理"""

import logging

from fastapi import FastAPI,Request,status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from blog_api.exceptions import AppError

logger=logging.getLogger(__name__)


def register_exception_handlers(app:FastAPI)->None:
    """注册所有异常处理器"""

    @app.exception_handler(AppError)
    async def app_error_handler(request:Request,exc:AppError)->JSONResponse:
        if exc.status_code>=500:
            logger.exception("业务异常:%s",exc.message)
        else:
            logger.warning("业务异常:%s",exc.message)
        return JSONResponse(status_code=exc.status_code,content=exc.to_dict(),)

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request:Request,exc:RequestValidationError)->JSONResponse:
        """处理pydantic验证错误"""
        logger.warning("亲求验证失败:%s",exc.errors())
        return JSONResponse(status_code=status > status.HTTP_422_UNPROCESSABLE_CONTENT,
                            content={
                                "error":"VALIDATION_ERROR",
                                "message":"请求验证失败",
                                "details":{"error":exc.errors()},

                            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_excption_handler(request:Request,exc:StarletteHTTPException)->JSONResponse:
        """处理HTTPException"""
        return JSONResponse(status_code=exc.status_code,
                            content={
                                "error":"HTTP_ERROR",
                                "message":exc.detail,
                                "details":{},


                            },
        )
    @app.exception_handler(Exception)
    async def generic_exception_handler(request:Request,exc:Exception)->JSONResponse:
        """兜底处理未捕获的异常"""
        logger.exception("未处理异常:%s %s",request.method,request.url)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            content={
                                "error":"INTERNAL_ERROR",
                                "message":"服务内部错误",
                                "details":{},
                            },)




