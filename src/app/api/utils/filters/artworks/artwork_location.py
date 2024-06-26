from typing import Optional

from pydantic import ConfigDict, Field

from app.api.utils.libs.fastapi_filter.contrib.sqlalchemy import Filter
from app.modules.artworks.models.artwork_location import ArtworkLocation


class ArtworkLocationFilter(Filter):
    model_config = ConfigDict(populate_by_name=True)

    order_by: Optional[list[str]] = Field(None)
    artwork__artist__username__ilike: Optional[str] = Field(None, alias="artistUsername")

    search: Optional[str] = None

    class Constants(Filter.Constants):
        model = ArtworkLocation
        search_model_fields = [
            "artwork__title",
            "artwork__festival",
            "artwork__artist__username",
        ]

    # class Config:
    #     populate_by_name = True
