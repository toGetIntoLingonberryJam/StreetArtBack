from enum import Enum
from typing import Dict, Union, Optional

from pydantic import BaseModel


# TODO: Обработка Response моделек тут для стандартизирования
class ErrorModel(BaseModel):
    detail: Union[str, Dict[str, str]]


class ErrorCodeReasonModel(BaseModel):
    code: str
    reason: str


class ErrorCode(str, Enum):
    INVALID_IMAGE_FILE_EXTENSION = "INVALID_IMAGE_FILE_EXTENSION"
    OBJECT_NOT_FOUND = "OBJECT_NOT_FOUND"
    NO_ACCESS_TO_RESOURCE = "NO_ACCESS_TO_RESOURCE"
    GATEWAY_TIMEOUT = "GATEWAY_TIMEOUT"
    INCORRECT_ROUTE_COORDINATES = "INCORRECT_ROUTE_COORDINATES"


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
                            "detail": generate_detail(
                                error_code=error_code, message=message, data=data
                            )
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
        "message": message,
    }

    # Добавляем ключ "data" в словарь только если он был передан
    if data is not None:
        detail["data"] = data

    return detail
