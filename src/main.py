from fastapi import FastAPI

from auth.auth_config import register_router, auth_router
from db_config import create_db_and_tables

app = FastAPI()


@app.on_event('on_startup')
async def on_startup():
    await create_db_and_tables()


on_startup()

app.include_router(register_router)

app.include_router(auth_router)
