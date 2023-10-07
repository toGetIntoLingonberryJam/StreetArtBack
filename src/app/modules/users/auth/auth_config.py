from fastapi_users.authentication import AuthenticationBackend, BearerTransport
from fastapi_users.authentication import JWTStrategy

from config import SECRET_KEY_JWT


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET_KEY_JWT, lifetime_seconds=None)  #, lifetime_seconds=60 * 60


bearer_transport = BearerTransport(tokenUrl='/auth/login')

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)






