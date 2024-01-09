from app.api.utils.libs.fastapi_filter.contrib.sqlalchemy import Filter
from fastapi_pagination import Params
from sqlalchemy import exc
from sqlalchemy.exc import NoResultFound

from app.modules.festivals.schemas import FestivalCreateSchema
from app.utils.exceptions import ObjectNotFoundException
from app.utils.unit_of_work import UnitOfWork


class FestivalService:
    async def get_festival_by_id(self, uow: UnitOfWork, festival_id: int):
        try:
            async with uow:
                festival = await uow.festival.get(festival_id)
                return festival
        except exc.NoResultFound:
            raise ObjectNotFoundException("Фестиваль не найден.")

    async def create_festival(
        self, uow: UnitOfWork, festival_schema: FestivalCreateSchema
    ):
        async with uow:
            festival = await uow.festival.create(festival_schema)
            await uow.commit()
            await uow.session.refresh(festival)
            return festival

    async def get_all_festival(
        self,
        uow: UnitOfWork,
        pagination: Params | None = None,
        filters: Filter | None = None,
        **filter_by
    ):
        async with uow:
            offset: int = 0
            limit: int | None = None

            if pagination:
                pagination_raw_params = pagination.to_raw_params()
                offset = pagination_raw_params.offset
                limit = pagination_raw_params.limit

            festivals = await uow.festival.get_all(
                offset=offset, limit=limit, filters=filters, filter_by=filter_by
            )
            return festivals

    async def delete_festival(self, uow: UnitOfWork, festival_id: int):
        async with uow:
            await uow.festival.delete(festival_id)

    async def update_artwork_festival(
        self, uow: UnitOfWork, artwork_id: int, festival_id: int
    ):
        async with uow:
            festival = await self.get_festival_by_id(uow, festival_id)
            try:
                artwork = await uow.artworks.edit(
                    artwork_id, {"festival_id": festival.id}
                )
                await uow.commit()
                return artwork
            except NoResultFound:
                raise ObjectNotFoundException("Арт-объект не найден.")
