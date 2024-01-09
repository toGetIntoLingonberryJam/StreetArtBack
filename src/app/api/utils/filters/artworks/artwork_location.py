from typing import Optional

from pydantic import Field
from app.api.utils.libs.fastapi_filter.contrib.sqlalchemy import Filter
from app.modules.artworks.models.artwork_location import ArtworkLocation


class ArtworkLocationFilter(Filter):
    order_by: Optional[list[str]] = Field(None)
    artwork__artist__username__ilike: Optional[str] = Field(
        None, alias="artistUsername"
    )

    search: Optional[str] = None

    class Constants(Filter.Constants):
        model = ArtworkLocation
        search_model_fields = ["title", "festival", "artist__username"]

    class Config:
        populate_by_name = True
