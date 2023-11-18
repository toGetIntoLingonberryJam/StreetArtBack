from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.admin_panel.apanel import AdminPanel
from app.api.routes import router

from app.db import engine, redis

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

app = FastAPI()


@app.on_event("startup")
async def startup():
    # # Проверяем, существует ли директория "static" и создаем её, если отсутствует
    # save_dir = Path("static/")
    # save_dir.mkdir(parents=True, exist_ok=True)
    #
    # # Монтируем статические файлы из директории "static"
    # app.mount("/static", StaticFiles(directory="static"), name="static")

    # Include routers
    app.include_router(router)

    # Initialize AdminPanel
    AdminPanel(app, engine)

    # Позволяет использовать декоратор @cache(sec), из fastapi_cache.decorator, кэшируя уникальный запрос-ответ в redis
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")



