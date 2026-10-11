"""自定义异常"""

from typing import Any


class AppError(Exception):
    """所有应用异常的基类"""

    status_code: int = 400
    error_code: str = "APP_ERROR"

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)

    def to_dict(self) -> dict[str, Any]:
        return {"error": self.error_code, "message": self.message, "details": self.details}


# ==========4xx客户端错误==========
class ValidationError(AppError):
    """输入验证失败"""

    status_code: int = 422
    error_code: str = "VALIDATION_ERROR"

    def __init__(self, field: str, message: str):
        self.field = field
        super().__init__(f"{field}:{message}", details={"field": field})


class BadRequestError(AppError):
    """亲求不合法"""

    status_code: int = 400
    error_code: str = "BadRequestError"


class UnauthorizedError(AppError):
    """未认证"""

    status_code: int = 401
    error_code: str = "UnauthorizedError"


class ForbiddenError(AppError):
    """无权限"""

    status_code: int = 403
    error_code: str = "ForbiddenError"


class NotFoundError(AppError):
    """资源不存在"""

    status_code: int = 404
    error_code: str = "NOT_FOUND"

    def __init__(self, resource: str, identifier: Any):
        self.resource = resource
        self.identifier = identifier
        super().__init__(
            f"{resource}:{identifier}不存在",
            details={"resource": resource, "identifier": str(identifier)},
        )


class ConflictError(AppError):
    """资源冲突"""

    status_code: int = 409
    error_code: str = "ConflictError"


# =======5xx服务端错误===========


class InternalError(AppError):
    """内部错误"""

    status_code: int = 500
    error_code: str = "InternalError"


class ExceptionServiceError(AppError):
    """外部服务错误"""

    status_code: int = 502
    error_code: str = "ExceptionServiceError"

    def __init__(self, service: str, message: str):
        self.service = service
        super().__init__(f"{service}:{message}", details={"service": service})
