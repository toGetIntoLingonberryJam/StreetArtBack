import os

from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
# DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"

SECRET_KEY_JWT = os.getenv("SECRET_KEY_JWT")
SECRET_VERIFICATION_TOKEN = os.getenv("SECRET_VERIFICATION_TOKEN")
SECRET_RESET_TOKEN = os.getenv("SECRET_RESET_TOKEN")
