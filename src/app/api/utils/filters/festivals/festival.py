from typing import Optional

from pydantic import Field

from app.api.utils.libs.fastapi_filter.contrib.sqlalchemy import Filter
from app.modules.festivals.models import Festival


class FestivalFilter(Filter):
    search: Optional[str] = None
    order_by: Optional[list[str]] = Field(None, exclude=True)

    class Constants(Filter.Constants):
        model = Festival
        search_model_fields = ["name", "description"]

    class Config:
        populate_by_name = True