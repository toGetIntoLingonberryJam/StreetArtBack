from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    RedisStrategy,
)

from app.db import redis


def get_redis_strategy() -> RedisStrategy:
    return RedisStrategy(redis, lifetime_seconds=None)


bearer_transport = BearerTransport(tokenUrl="/v1/auth/login")

auth_backend = AuthenticationBackend(
    name="streetart",
    transport=bearer_transport,
    get_strategy=get_redis_strategy,
)
