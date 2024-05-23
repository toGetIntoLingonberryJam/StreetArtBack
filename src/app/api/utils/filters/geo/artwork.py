from typing import Optional

from fastapi import Query
from pydantic import ConfigDict, Field

from app.api.utils.libs.fastapi_filter.contrib.sqlalchemy import Filter
from app.modules.artworks.models.artwork import Artwork


class GeoArtworkFilter(Filter):
    model_config = ConfigDict(populate_by_name=True)

    id__in: list[int] = Field(alias="artwork_ids")

    class Constants(Filter.Constants):
        model = Artwork
