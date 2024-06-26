from typing import Optional

from pydantic import ConfigDict, Field

from app.api.utils.libs.fastapi_filter.contrib.sqlalchemy import Filter
from app.modules.models import Artist


class ArtistFilter(Filter):
    model_config = ConfigDict(populate_by_name=True)

    search: Optional[str] = None
    order_by: Optional[list[str]] = Field(None, exclude=True)

    class Constants(Filter.Constants):
        model = Artist
        search_model_fields = ["name", "description"]
