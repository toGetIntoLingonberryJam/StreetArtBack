from fastapi_users import FastAPIUsers
from fastapi_users.authentication import AuthenticationBackend, BearerTransport
from fastapi_users.authentication import JWTStrategy

from config import SECRET_KEY_JWT
from auth.manager import get_user_manager
from auth.schemas import UserCreate, UserRead
from auth.user import User

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET_KEY_JWT, lifetime_seconds=60 * 60)


bearer_transport = BearerTransport(tokenUrl='/auth/jwt/login')

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

current_user = fastapi_users.current_user()

register_router = fastapi_users.get_register_router(UserRead, UserCreate)
auth_router = fastapi_users.get_auth_router(auth_backend)