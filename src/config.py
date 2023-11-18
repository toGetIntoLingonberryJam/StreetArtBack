import os

from dotenv import load_dotenv

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    STATIC_IMAGE_FOLDER: str = "static/images/"
    BACKEND_URL: str = "https://streetartback.onrender.com/"  # Значение по умолчанию


# Создание экземпляра настроек
settings = Settings()

# TODO: Переделать в pydantic_settings

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
# DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"

REDIS_URL = os.getenv("REDIS_URL")

SECRET_VERIFICATION_TOKEN = os.getenv("SECRET_VERIFICATION_TOKEN")
SECRET_RESET_TOKEN = os.getenv("SECRET_RESET_TOKEN")

YANDEX_DISK_TOKEN = os.getenv("YANDEX_DISK_TOKEN")
YANDEX_DISK_IMAGES_FOLDER = os.getenv("YANDEX_DISK_IMAGES_FOLDER")

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

BACKEND_URL = os.getenv("BACKEND_URL")
