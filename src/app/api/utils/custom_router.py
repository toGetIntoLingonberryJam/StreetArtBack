from typing import get_type_hints

from fastapi import APIRouter

from app.modules.models import Artist, Moderator, User

USER_ROLES = [User, Artist, Moderator]


class CustomAPIRouter(APIRouter):

    def add_api_route(self, path: str, endpoint, **kwargs):
        role = self._get_user_role(endpoint)
        if role:
            endpoint_name = self._format_endpoint_name(endpoint.__name__, role)
        else:
            endpoint_name = endpoint.__name__
        kwargs.pop(
            "name", None
        )  # Удаление аргумента 'name', если он есть (а есть он всегда)
        super().add_api_route(path, endpoint, **kwargs, name=endpoint_name)

    @staticmethod
    def _format_endpoint_name(func_name: str, user_role: str) -> str:
        separator = "⮜"
        return f"{func_name} {separator} {user_role}"

    @staticmethod
    def _get_user_role(endpoint) -> str | None:
        hints = get_type_hints(endpoint)
        role = next((role for role in USER_ROLES if role in hints.values()), None)
        return role.__name__ if role else None
