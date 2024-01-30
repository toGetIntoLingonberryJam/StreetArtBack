from fastapi import FastAPI
from fastapi_pagination import add_pagination

from app.admin_panel.apanel import AdminPanel
from app.api.routes import router

from app.db import engine, redis

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend


app = FastAPI(title="StreetArtWitnessesAPI", version="2.0.0")


@app.on_event("startup")
async def startup():
    # Include routers
    app.include_router(router)

    # Initialize AdminPanel
    AdminPanel(app, engine)

    # Adding a pagination module to an application
    add_pagination(app)

    # Позволяет использовать декоратор @cache(sec), из fastapi_cache.decorator, кэшируя уникальный запрос-ответ в redis
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
