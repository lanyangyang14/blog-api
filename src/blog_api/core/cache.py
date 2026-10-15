"""Redis 缓存。"""

import json
import logging
from typing import Any

import redis

from blog_api.config import settings

logger = logging.getLogger(__name__)


class Cache:
    """简单的 Redis 缓存封装。"""

    def __init__(self, url: str | None = None):
        self.client: redis.Redis[str] = redis.from_url(
            url or settings.redis_url,
            decode_responses=True,
        )

    def get(self, key: str) -> Any | None:
        try:
            value = self.client.get(key)
            if value is None:
                return None
            return json.loads(value)
        except Exception:
            logger.exception("缓存读取失败: %s", key)
            return None

    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        try:
            self.client.setex(key, ttl, json.dumps(value, default=str))
        except Exception:
            logger.exception("缓存写入失败: %s", key)

    def delete(self, key: str) -> None:
        try:
            self.client.delete(key)
        except Exception:
            logger.exception("缓存删除失败: %s", key)

    def delete_pattern(self, pattern: str) -> None:
        try:
            keys = list(self.client.keys(pattern))
            if keys:
                self.client.delete(*keys)
        except Exception:
            logger.exception("缓存批量删除失败: %s", pattern)

    def incr(self, key: str) -> int:
        """自增。"""
        try:
            return int(self.client.incr(key))
        except Exception:
            logger.exception("缓存自增失败: %s", key)
            return 0

    def expire(self, key: str, seconds: int) -> None:
        """设置过期。"""
        try:
            self.client.expire(key, seconds)
        except Exception:
            logger.exception("缓存设置过期失败: %s", key)


cache = Cache()
