from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.admin_panel.apanel import AdminPanel
from app.api import routes
from app.modules.users.auth.auth_router import auth_router
from app.modules.users.fastapi_users_routes import user_router
from app.db import create_db_and_tables, engine, drop_db_and_tables

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


# Events

@app.on_event("startup")
async def on_startup():
    # Not needed if you setup a migration system like Alembic
    # await drop_db_and_tables()

    await create_db_and_tables()


# Includes

app.include_router(auth_router)
app.include_router(user_router)
# app.include_router(artwork_router)

for router in routes.all_routers:
    app.include_router(router)

# Initialize AdminPanel
AdminPanel(app, engine)

