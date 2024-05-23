from typing import Optional

from pydantic import ConfigDict, Field

from app.api.utils.libs.fastapi_filter.contrib.sqlalchemy import Filter
from app.modules.artworks.models.artwork import Artwork


class ArtworkFilter(Filter):
    model_config = ConfigDict(populate_by_name=True)

    order_by: Optional[list[str]] = Field(None)
    artist__username__ilike: Optional[str] = Field(None, alias="artistUsername")
    status__in: Optional[list[str]] = Field(None, alias="status")
    year_created__gte: Optional[int] = Field(None, alias="yearCreatedFrom")
    year_created__lte: Optional[int] = Field(None, alias="yearCreatedTo")

    search: Optional[str] = Field(None)

    class Constants(Filter.Constants):
        model = Artwork
        ordering_model_fields = ["id", "status", "year_created"]
        search_model_fields = ["title", "festival__name", "artist__name"]
