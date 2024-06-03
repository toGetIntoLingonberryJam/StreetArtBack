from pydantic import PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="/etc/secrets/.env", env_file_encoding="utf-8"
    )

    mode: str

    db_host: str
    db_port: int
    db_pass: str
    db_name: str
    db_user: str
    db_sslmode: str
    redis_url: RedisDsn
    secret_key_jwt: str
    secret_verification_token: str
    secret_reset_token: str
    email_sender: str
    email_password: str
    backend_url: str

    queue_url: str
    aws_access_key_id: str
    aws_secret_access_key: str
    bucket_name: str

    @property
    def database_url(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.db_user,
            password=self.db_pass,
            host=self.db_host,
            port=self.db_port,
            path=f"{self.db_name}",
            query=f"ssl={self.db_sslmode}"
        )


settings = Settings()
print(f"Settings Mode: {settings.mode}")
print(f"DB url: {settings.database_url}")
