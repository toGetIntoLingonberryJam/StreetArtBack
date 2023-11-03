from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.admin_panel.apanel import AdminPanel
from app.api import routes
from app.modules.users.auth.auth_router import auth_router
from app.modules.users.fastapi_users_routes import user_router

from app.db import engine


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

# Includes

app.include_router(auth_router)
app.include_router(user_router)

for router in routes.all_routers:
    app.include_router(router)

# Initialize AdminPanel
AdminPanel(app, engine)

