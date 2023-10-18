import redis as redis
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, RedisStrategy

from config import REDIS_URL

redis = redis.asyncio.from_url(REDIS_URL, decode_responses=True)


def get_redis_strategy() -> RedisStrategy:
    return RedisStrategy(redis, lifetime_seconds=None)


bearer_transport = BearerTransport(tokenUrl='/auth/login')

auth_backend = AuthenticationBackend(
    name="streetart",
    transport=bearer_transport,
    get_strategy=get_redis_strategy,
)
