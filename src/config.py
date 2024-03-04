from functools import lru_cache
from pydantic import PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8"
    )

    db_host: str
    db_port: int
    db_pass: str
    db_name: str
    db_user: str
    redis_url: RedisDsn
    secret_key_jwt: str
    secret_verification_token: str
    secret_reset_token: str
    yandex_disk_token: str
    yandex_disk_images_folder: str
    email_sender: str
    email_password: str
    backend_url: str

    @property
    def database_url(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.db_user,
            password=self.db_pass,
            host=self.db_host,
            port=self.db_port,
            path=f"{self.db_name}",
        )


settings = Settings()

# @lru_cache
# def settings -> Settings:
#     return Settings()
