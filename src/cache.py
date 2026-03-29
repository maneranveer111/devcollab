# src/cache.py
# Redis caching and rate limiting utilities for DevCollab

import redis
import json
from fastapi import HTTPException, status, Request


# ─── Redis connection ─────────────────────────────────────────────────────────

redis_client = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True
)


# ─── Cache key constants ──────────────────────────────────────────────────────

USERS_CACHE_KEY = "devcollab:users:all"
PROJECTS_CACHE_KEY = "devcollab:projects:all"
CACHE_EXPIRE_SECONDS = 300  # 5 minutes


# ─── Cache functions ──────────────────────────────────────────────────────────

def get_cached_data(key: str):
    """Get data from Redis cache. Returns None if not found or Redis is down."""
    try:
        data = redis_client.get(key)
        if data:
            return json.loads(data)
        return None
    except Exception:
        return None


def set_cached_data(key: str, data, expire: int = CACHE_EXPIRE_SECONDS):
    """Store data in Redis cache with expiration time."""
    try:
        redis_client.setex(key, expire, json.dumps(data))
    except Exception:
        pass


def invalidate_cache(key: str):
    """Delete a cache key. Called when data changes."""
    try:
        redis_client.delete(key)
    except Exception:
        pass


def check_redis_connection() -> bool:
    """Check if Redis is reachable."""
    try:
        redis_client.ping()
        return True
    except Exception:
        return False


# ─── Rate limiting ────────────────────────────────────────────────────────────

def check_rate_limit(
    identifier: str,
    limit: int,
    window_seconds: int
) -> bool:
    """
    Check if identifier has exceeded rate limit.
    Returns True if allowed, False if blocked.

    identifier     → who is making the request (username or IP)
    limit          → max requests allowed in the window
    window_seconds → time window in seconds
    """
    try:
        key = f"rate_limit:{identifier}"

        current = redis_client.get(key)

        if current is None:
            # First request — create counter with expiration
            redis_client.setex(key, window_seconds, 1)
            return True

        if int(current) >= limit:
            return False

        # Increment counter (keeps existing TTL)
        redis_client.incr(key)
        return True

    except Exception:
        return True


def rate_limit_login(request: Request):
    """
    Rate limit: 5 login attempts per minute per IP.
    Prevents brute force password attacks.
    """
    identifier = f"login:{request.client.host}"

    if not check_rate_limit(identifier, limit=5, window_seconds=60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please wait 1 minute."
        )