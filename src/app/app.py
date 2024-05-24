from contextlib import asynccontextmanager
import fastapi_cdn_host
from fastapi_cdn_host import CdnHostEnum

from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_pagination import add_pagination

from app.admin_panel.apanel import AdminPanel
from app.api.routes import router
from app.db import engine, redis


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    """Запускаем код до и после запуска приложения"""

    # Include routers
    fastapi_app.include_router(router)
    # Initialize AdminPanel
    AdminPanel(fastapi_app, engine)
    # Adding a pagination module to an application
    add_pagination(fastapi_app)

    # Проверка подключения к Redis. Иначе - краш.
    # ToDo: сделать красивый вывод ошибки, а не стандартный Traceback
    await redis.ping()
    # Позволяет использовать декоратор @cache(sec), из fastapi_cache.decorator, кэшируя уникальный запрос-ответ в redis
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

    yield  # Возвращаем работу приложению
    # тут можно выполнить код после завершения приложения


app = FastAPI(title="StreetArtWitnessesAPI", version="2.0.0", lifespan=lifespan)

# Will use `unpkg.com` to replace the `cdn.jsdelivr.net/npm`
fastapi_cdn_host.patch_docs(app=app, docs_cdn_host=CdnHostEnum.unpkg)
