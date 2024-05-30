from pydantic import BaseModel, ConfigDict


class ModeratorBaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str


class ModeratorCreateSchema(ModeratorBaseSchema):
    user_id: int = None


class ModeratorReadSchema(ModeratorBaseSchema):
    id: int
    user_id: int = None


