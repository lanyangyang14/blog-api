"""Redis 缓存（异步）。"""

import json
import logging
from typing import Any

import redis.asyncio as redis

from blog_api.config import settings
from blog_api.core.metrics import cache_hits_total, cache_misses_total

logger = logging.getLogger(__name__)


class Cache:
    """Redis 缓存封装（异步）。"""

    def __init__(self, url: str | None = None):
        self.client: redis.Redis[str] = redis.from_url(
            url or settings.redis_url,
            decode_responses=True,
        )

    async def get(self, key: str) -> Any | None:
        key_prefix = key.split(":")[0]  # 如 "post"
        try:
            value = await self.client.get(key)
            if value is None:
                cache_misses_total.labels(key_prefix=key_prefix).inc()
                return None
            cache_hits_total.labels(key_prefix=key_prefix).inc()
            return json.loads(value)
        except Exception:
            logger.exception("缓存读取失败: %s", key)
            return None

    async def set(self, key: str, value: Any, ttl: int = 300) -> None:
        try:
            await self.client.setex(key, ttl, json.dumps(value, default=str))
        except Exception:
            logger.exception("缓存写入失败: %s", key)

    async def delete(self, key: str) -> None:
        try:
            await self.client.delete(key)
        except Exception:
            logger.exception("缓存删除失败: %s", key)

    async def delete_pattern(self, pattern: str) -> None:
        try:
            keys = await self.client.keys(pattern)
            if keys:
                await self.client.delete(*keys)
        except Exception:
            logger.exception("缓存批量删除失败: %s", pattern)

    async def incr(self, key: str) -> int:
        try:
            return await self.client.incr(key)
        except Exception:
            logger.exception("缓存自增失败: %s", key)
            return 0

    async def expire(self, key: str, seconds: int) -> None:
        try:
            await self.client.expire(key, seconds)
        except Exception:
            logger.exception("缓存设置过期失败: %s", key)


cache = Cache()
