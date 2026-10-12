""" "写测试"""

from blog_api.config import Settings, get_settings


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


def test_log_level_uppercase():
    settings = Settings(secret_key="a" * 32, log_level="debug")
    assert settings.log_level == "DEBUG"
