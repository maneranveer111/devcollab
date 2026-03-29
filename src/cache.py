import redis
import json

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