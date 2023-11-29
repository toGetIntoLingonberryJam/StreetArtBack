from enum import Enum
from typing import Dict, Union, Optional

from pydantic import BaseModel


class ErrorModel(BaseModel):
    detail: Union[str, Dict[str, str]]


class ErrorCodeReasonModel(BaseModel):
    code: str
    reason: str


class ErrorCode(str, Enum):
    INVALID_IMAGE_FILE_EXTENSION = "INVALID_IMAGE_FILE_EXTENSION"
    OBJECT_NOT_FOUND = "OBJECT_NOT_FOUND"
    # REGISTER_INVALID_PASSWORD = "REGISTER_INVALID_PASSWORD"
    # REGISTER_USER_ALREADY_EXISTS = "REGISTER_USER_ALREADY_EXISTS"
    # OAUTH_NOT_AVAILABLE_EMAIL = "OAUTH_NOT_AVAILABLE_EMAIL"
    # OAUTH_USER_ALREADY_EXISTS = "OAUTH_USER_ALREADY_EXISTS"
    # LOGIN_BAD_CREDENTIALS = "LOGIN_BAD_CREDENTIALS"
    # LOGIN_USER_NOT_VERIFIED = "LOGIN_USER_NOT_VERIFIED"
    # RESET_PASSWORD_BAD_TOKEN = "RESET_PASSWORD_BAD_TOKEN"
    # RESET_PASSWORD_INVALID_PASSWORD = "RESET_PASSWORD_INVALID_PASSWORD"
    # VERIFY_USER_BAD_TOKEN = "VERIFY_USER_BAD_TOKEN"
    # VERIFY_USER_ALREADY_VERIFIED = "VERIFY_USER_ALREADY_VERIFIED"
    # UPDATE_USER_EMAIL_ALREADY_EXISTS = "UPDATE_USER_EMAIL_ALREADY_EXISTS"
    # UPDATE_USER_INVALID_PASSWORD = "UPDATE_USER_INVALID_PASSWORD"


def generate_response(
    error_model, error_code, summary: str, message: str, data: Optional[dict] = None
):
    response = {
        "model": error_model,
        "content": {
            "application/json": {
                "examples": {
                    error_code: {
                        "summary": summary,
                        "value": {
                            "detail": generate_detail(error_code=error_code, message=message, data=data)
                        },
                    },
                }
            }
        },
    }

    return response


def generate_detail(error_code, message: str, data: Optional[dict] = None):
    detail = {
        "code": error_code,
        "msg": message,
    }

    # Добавляем ключ "data" в словарь только если он был передан
    if data is not None:
        detail["data"] = data

    return detail
