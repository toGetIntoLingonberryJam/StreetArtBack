from pydantic import BaseModel, ConfigDict


class ArtistCard(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
