from fastapi_users import FastAPIUsers

from app.modules.users.auth.auth_config import auth_backend
from app.modules.users.manager import get_user_manager
from app.modules.users.models.user import User

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

current_user = fastapi_users.current_user()
