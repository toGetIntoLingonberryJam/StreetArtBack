import logging
from contextlib import asynccontextmanager
import fastapi_cdn_host
from fastapi_cdn_host import CdnHostEnum

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_pagination import add_pagination

from app.admin_panel.apanel import AdminPanel
from app.api.routes import router
from app.db import engine, redis
from logger_config import logger


async def check_connections():
    try:
        # Проверка подключения к Redis
        await redis.ping()
    except Exception as e:
        logger.error("Ошибка подключения к Redis: %s", str(e))
        raise RuntimeError("Не удалось подключиться к Redis. Сервер остановлен.") from e

    try:
        # Проверка подключения к PostgreSQL
        conn = await engine.connect()
        await conn.aclose()
    except Exception as e:
        logger.error("Ошибка подключения к PostgreSQL: %s", str(e))
        raise RuntimeError(
            "Не удалось подключиться к PostgreSQL. Сервер остановлен."
        ) from e


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    """Запускаем код до и после запуска приложения"""
    # Проверка подключения к Базам Данных. В случае неудачи - краш сервера.
    await check_connections()

    # Include routers
    fastapi_app.include_router(router)
    # Initialize AdminPanel
    AdminPanel(fastapi_app, engine)
    # Adding a pagination module to an application
    add_pagination(fastapi_app)

    # Позволяет использовать декоратор @cache(sec), из fastapi_cache.decorator, кэшируя уникальный запрос-ответ в redis
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

    yield  # Возвращаем работу приложению
    # тут можно выполнить код после завершения приложения


app = FastAPI(title="StreetArtWitnessesAPI", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Will use `unpkg.com` to replace the `cdn.jsdelivr.net/npm`
fastapi_cdn_host.patch_docs(app=app, docs_cdn_host=CdnHostEnum.unpkg)
