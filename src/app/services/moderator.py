from typing import Optional

from sqlalchemy.exc import NoResultFound

from app.api.utils.paginator import MyParams
from app.modules.moderation.schemas import ModeratorCreateSchema
from app.utils.unit_of_work import UnitOfWork


class ModeratorsService:
    @staticmethod
    async def get_moderator_by_user_id(uow: UnitOfWork, user_id: int):
        async with uow:
            moderator = await uow.moderator.filter(user_id=user_id)
            if not moderator:
                raise NoResultFound
            return moderator[0]  # list так как filter


    @staticmethod
    async def get_moderators(uow: UnitOfWork, pagination: Optional[MyParams] = None):
        async with uow:
            moderators = await uow.moderator.get_all(offset=pagination.offset, limit=pagination.limit)
            return moderators

    @staticmethod
    async def create_moderator(uow: UnitOfWork, moderator_schema: ModeratorCreateSchema):
        async with uow:
            moderator = await uow.moderator.create(moderator_schema)
            return moderator

    @staticmethod
    async def delete_moderator(uow: UnitOfWork, moderator_id: int):
        async with uow:
            await uow.moderator.delete(moderator_id)

