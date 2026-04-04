import redis
import json
import logging
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_redis_client = None


def get_redis():
    global _redis_client
    if _redis_client is None:
        try:
            _redis_client = redis.from_url(settings.redis_url, decode_responses=True)
            _redis_client.ping()
        except Exception as e:
            logger.warning(f"Redis unavailable: {e}")
            _redis_client = None
    return _redis_client


def cache_get(key: str):
    r = get_redis()
    if r is None:
        return None
    try:
        val = r.get(key)
        return json.loads(val) if val else None
    except Exception as e:
        logger.warning(f"Cache get error: {e}")
        return None


def cache_set(key: str, value, ttl: int = 60):
    r = get_redis()
    if r is None:
        return
    try:
        r.setex(key, ttl, json.dumps(value))
    except Exception as e:
        logger.warning(f"Cache set error: {e}")
