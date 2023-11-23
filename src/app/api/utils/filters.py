from datetime import datetime
from typing import Optional

from fastapi import Query
from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import field_validator, Field

from app.modules.artworks.models.artwork import Artwork


class ArtworkFilter(Filter):
    order_by: Optional[list[str]] = Field(None)
    status__in: Optional[list[str]] = Field(None, alias="status")
    year_created__gte: Optional[int] = Field(None, alias="yearCreatedFrom")
    year_created__lte: Optional[int] = Field(None, alias="yearCreatedTo")

    search: Optional[str] = None

    @field_validator("order_by")
    def restrict_sortable_fields(cls, value):
        if value is None:
            return None

        allowed_field_names = ["id", "status", "year_created"]

        for field_name in value:
            field_name = field_name.replace("+", "").replace("-", "")  #
            if field_name not in allowed_field_names:
                raise ValueError(f"You may only sort by: {', '.join(allowed_field_names)}")

        return value

    class Constants(Filter.Constants):
        model = Artwork
        # search_field_name = "custom_name_for_search"
        search_model_fields = ["title", "festival"]

    class Config:
        populate_by_name = True
