import redis
from app.core.config import settings

redis_client = redis.from_url(
    settings.REDIS_URL,
    decode_responses=True
)

def invalidate_cache(post_id: int | None = None):
    keys = redis_client.keys("posts:*")
    if keys:
        redis_client.delete(*keys)
    if post_id is not None:
        redis_client.delete(f"post:{post_id}")