from pydantic import BaseModel, ConfigDict


class ArtistCardSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
