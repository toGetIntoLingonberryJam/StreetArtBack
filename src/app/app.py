from fastapi import FastAPI
from app.modules.users.auth.auth_router import auth_router
from app.modules.users.fastapi_users_routes import user_router

app = FastAPI()

# Includes

app.include_router(auth_router)
app.include_router(user_router)
