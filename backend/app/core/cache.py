"""
Caching service with Redis and in-memory TTL fallback.
Ensures zero-downtime operation whether Redis is available or not.
"""
import time
import json
import logging
from typing import Any, Optional
import redis.asyncio as aioredis
from app.core.config import settings

logger = logging.getLogger("futuroscope.cache")


class InMemoryTTLCache:
    """Thread-safe and async-compatible in-memory cache with TTL expiration."""

    def __init__(self):
        self._store: dict[str, tuple[float, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        if key in self._store:
            expire_at, value = self._store[key]
            if time.time() < expire_at:
                return value
            else:
                del self._store[key]
        return None

    def set(self, key: str, value: Any, ttl_seconds: int = 180):
        self._store[key] = (time.time() + ttl_seconds, value)

    def clear(self):
        self._store.clear()


class CacheService:
    def __init__(self):
        self._redis_client: Optional[aioredis.Redis] = None
        self._memory_cache = InMemoryTTLCache()
        self._redis_available: bool = False

    async def initialize(self):
        """Attempts to connect to Redis, falls back gracefully to in-memory cache."""
        try:
            self._redis_client = aioredis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=2.0,
                socket_timeout=2.0
            )
            await self._redis_client.ping()
            self._redis_available = True
            logger.info("Connected to Redis cache successfully.")
        except Exception as e:
            self._redis_available = False
            logger.warning(
                f"Redis unavailable ({e}). Using robust In-Memory TTL Cache fallback."
            )

    async def close(self):
        if self._redis_client:
            try:
                if hasattr(self._redis_client, "aclose"):
                    await self._redis_client.aclose()
                else:
                    await self._redis_client.close()
            except Exception:
                pass

    async def get(self, key: str) -> Optional[Any]:
        if self._redis_available and self._redis_client:
            try:
                val = await self._redis_client.get(key)
                if val is not None:
                    return json.loads(val)
            except Exception as e:
                logger.warning(f"Redis get failed for {key}: {e}. Checking memory fallback.")
        return self._memory_cache.get(key)

    async def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None):
        ttl = ttl_seconds if ttl_seconds is not None else settings.CACHE_TTL_SECONDS
        serialized = json.dumps(value, default=str)

        # Always update in-memory cache as reliable backup
        self._memory_cache.set(key, value, ttl)

        if self._redis_available and self._redis_client:
            try:
                await self._redis_client.set(key, serialized, ex=ttl)
            except Exception as e:
                logger.warning(f"Redis set failed for {key}: {e}. Value saved to memory cache.")


# Singleton instance
cache = CacheService()
