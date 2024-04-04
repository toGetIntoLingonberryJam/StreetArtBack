import pytest
from fastapi import status
from httpx import AsyncClient

from app.modules.users.schemas import UserCreate


class User:
    username: str
    email: str
    password: str

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password


@pytest.mark.usefixtures("test_redis", "clear_database")
class TestAuth:
    user_schema = UserCreate(
        username="test", email="test@example.com", password="test-pass"
    )

    async def test_register(self, async_client: AsyncClient):

        response = await async_client.post(
            "/v1/auth/register",
            json={
                "username": self.user_schema.username,
                "email": self.user_schema.email,
                "password": self.user_schema.password,
            },
        )

        assert (
            response.status_code == status.HTTP_201_CREATED
        ), "Зарегистрировать пользователя не удалось"

    async def test_login(self, async_client: AsyncClient):
        # Регистрация пользователя в пустой базе данных путём вызова первого теста
        await self.test_register(async_client=async_client)

        # Аутентификация пользователя с использованием данных о зарегистрированном пользователе
        # Важный аспект! В библиотеке fastapi_users в эндпоинтах авторизации используется ключ "username", но
        # используется email, для того, чтобы не переопределять базовый OpenAPI (SwaggerUI) и не создавать
        # кастомную авторизацию OAuth2PasswordBearer
        response = await async_client.post(
            "/v1/auth/login",
            data={
                "username": self.user_schema.email,
                "password": self.user_schema.password,
            },
        )

        assert (
            response.status_code == status.HTTP_200_OK
        ), "Не удалось авторизовать пользователя"

        assert response.json()["access_token"]
        assert response.json()["token_type"] == "bearer"
