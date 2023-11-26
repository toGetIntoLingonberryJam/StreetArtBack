from fastapi import FastAPI, HTTPException
from fastapi_pagination import add_pagination

from app.admin_panel.apanel import AdminPanel
from app.api.routes import router

from app.db import engine, redis

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from app.utils.fastapi_responses.openapi import custom_openapi

app = FastAPI(title="StreetArtWitnessesAPI")


@app.on_event("startup")
async def startup():
    # Include routers
    app.include_router(router)

    # Initialize AdminPanel
    AdminPanel(app, engine)

    # Adding a pagination module to an application
    add_pagination(app)

    # Adding an HTTPExceptions handler to display in the documentation
    app.openapi = custom_openapi(app)

    # Позволяет использовать декоратор @cache(sec), из fastapi_cache.decorator, кэшируя уникальный запрос-ответ в redis
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
