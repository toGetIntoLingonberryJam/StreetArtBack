from fastapi import FastAPI
from app.modules.users.auth.auth_router import auth_router
from app.modules.users.fastapi_users_routes import user_router
from app.db import create_db_and_tables, drop_db_and_tables

app = FastAPI()


# Events

# @app.on_event("startup")
# async def on_startup():
#     # Not needed if you setup a migration system like Alembic
#     await create_db_and_tables()
#     # await drop_db_and_tables()


# Includes

app.include_router(auth_router)
app.include_router(user_router)
