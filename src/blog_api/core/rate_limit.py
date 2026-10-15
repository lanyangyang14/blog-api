"""简单的 Redis 限流。"""

import logging

from blog_api.core.cache import cache
from blog_api.exceptions import AppError

logger = logging.getLogger(__name__)


class RateLimitError(AppError):
    status_code = 429
    error_code = "RATE_LIMIT_EXCEEDED"

    def __init__(self, message: str = "请求过于频繁"):
        super().__init__(message)


def check_rate_limit(key: str, max_requests: int, window_seconds: int) -> None:
    """滑动窗口限流。

    Args:
        key: 限流键（如 `rate:user:1:like`）
        max_requests: 窗口内最多请求数
        window_seconds: 窗口秒数

    Raises:
        RateLimitError: 超限。
    """
    try:
        current = cache.incr(key)
        if current == 1:
            cache.expire(key, window_seconds)
        if current > max_requests:
            raise RateLimitError(f"请求过于频繁，请 {window_seconds} 秒后重试")
    except RateLimitError:
        raise
    except Exception:
        logger.exception("限流检查失败，放行")
