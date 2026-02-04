from typing import Optional, Any
import json
from redis import asyncio as aioredis

from ..core.config import settings


class RedisCache:
    """
    Redis cache manager for caching API responses and data
    """

    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None

    async def connect(self):
        """
        Connect to Redis server
        """
        self.redis = await aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )

    async def disconnect(self):
        """
        Close Redis connection
        """
        if self.redis:
            await self.redis.close()

    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        """
        if not self.redis:
            return None

        value = await self.redis.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None

    async def set(self, key: str, value: Any, expire: int = 300) -> bool:
        """
        Set value in cache with expiration time in seconds
        """
        if not self.redis:
            return False

        if not isinstance(value, str):
            value = json.dumps(value)

        return await self.redis.setex(key, expire, value)

    async def delete(self, key: str) -> bool:
        """
        Delete value from cache
        """
        if not self.redis:
            return False

        return await self.redis.delete(key) > 0

    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache
        """
        if not self.redis:
            return False

        return await self.redis.exists(key) > 0


cache = RedisCache()
