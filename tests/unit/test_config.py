""" "写测试"""

import pytest

from blog_api.config import Settings, get_settings, settings
from blog_api.exceptions import ValidationError


def test_get_settings_load():
    """配置能加载"""
    settings = get_settings()
    assert settings.app_name == "blog-api"
    assert settings.secret_key
    assert len(settings.secret_key) >= 32
    assert settings.database_url


def test_settings_is_development():
    """开发环境测试"""
    settings = get_settings()
    assert settings.is_development is True
    assert settings.is_production is False


def test_cors_origins_parsing(monkeypatch):
    """CORS从字符串解析"""
    settings = Settings(
        secret_key="a" * 32,
        cors_origins="http://a.com,http://b.com",
    )
    assert settings.cors_origins == ["http://a.com", "http://b.com"]


def test_log_level_uppercase(monkeypatch):
    """日志级别大写"""
    Settings(secret_key="a" * 32, log_level="DEBUG")
    assert settings.log_level == "DEBUG"


def test_secret_key_too_short(monkeypatch):
    """SECRET_KEY太短报错"""
    with pytest.raises(ValidationError):
        Settings(secret_key="short")
