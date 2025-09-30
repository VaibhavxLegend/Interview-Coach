from __future__ import annotations
from typing import Optional
from redis import Redis
from .config import settings

_redis: Optional[Redis] = None


def get_redis() -> Optional[Redis]:
    global _redis
    if _redis is not None:
        return _redis
    try:
        _redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
        # ping to verify
        _redis.ping()
        return _redis
    except Exception:
        return None
