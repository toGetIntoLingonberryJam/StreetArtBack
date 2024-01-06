from typing import List

from pydantic import BaseModel, ConfigDict, HttpUrl


class ArtistBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    description: str
    links: List[HttpUrl]