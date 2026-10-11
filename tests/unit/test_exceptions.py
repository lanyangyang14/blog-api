""" "测试异常"""

from blog_api.exceptions import (
    NotFoundError,
    ValidationError,
)


def test_validation_error():
    """Validation Error携带字段信息"""
    exc = ValidationError("email", "格式错误")
    assert exc.status_code == 422
    assert exc.error_code == "VALIDATION_ERROR"
    assert exc.field == "email"
    assert "email" in exc.message


def test_not_found_error():
    """NotFoundError携带资源信息"""
    exc = NotFoundError("User", 123)
    assert exc.status_code == 404
    assert exc.resource == "User"
    assert exc.identifier == 123


def test_to_dict():
    """异常能转字典"""
    exc = ValidationError("email", "格式错误")
    data = exc.to_dict()
    assert data["error"] == "VALIDATION_ERROR"
    assert data["details"]["field"] == "email"
