from sqlalchemy.exc import NoResultFound

from app.utils.unit_of_work import UnitOfWork


class ModeratorsService:
    @staticmethod
    async def get_moderator_by_user_id(uow: UnitOfWork, user_id: int):
        async with uow:
            moderator = await uow.moderator.filter(user_id=user_id)
            if not moderator:
                raise NoResultFound
            return moderator[0]  # list так как filter
