from fastapi_filter.contrib.sqlalchemy import Filter
from fastapi_pagination import Params
from sqlalchemy import exc
from sqlalchemy.exc import NoResultFound

from app.modules.artists.schemas.artist import ArtistCreate
from app.utils.exceptions import UserNotFoundException, IncorrectInput, ObjectNotFoundException
from app.utils.unit_of_work import UnitOfWork


class ArtistsService:
    async def get_artist_by_id(self, uow: UnitOfWork, artist_id: int):
        try:
            async with uow:
                artist = await uow.artist.get(artist_id)
                return artist
        except exc.NoResultFound:
            return None

    async def create_artist(self, uow: UnitOfWork, artist_schema: ArtistCreate):
        async with uow:
            if artist_schema.user_id:
                try:
                    user = await uow.users.get(artist_schema.user_id)
                    if not user.is_verified:
                        raise IncorrectInput("Пользователь не верифициован.")
                except NoResultFound:
                    raise UserNotFoundException("Пользователь не найден.")

                artist_user = await uow.artist.filter(user_id=user.id)
                if artist_user:
                    raise IncorrectInput("Пользователь уже является художником.")
                user = await uow.users.edit(user.id, {"is_artist": True})
            else:
                artist_schema.user_id = None
            artist = await uow.artist.create(artist_schema)
            await uow.commit()
            return artist

    async def get_all_artist(self,
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
            artists = await uow.artist.get_all(offset=offset,
                                               limit=limit,
                                               filters=filters,
                                               filter_by=filter_by)
            return artists

    async def delete_artist(self, uow: UnitOfWork, artist_id: int):
        async with uow:
            await uow.artist.delete(artist_id)

    async def get_artist_by_user_id(self, uow: UnitOfWork, user_id: int):
        async with uow:
            artist = uow.artist.filter(user_id=user_id)
            return artist

    async def update_artwork_artist(self, uow: UnitOfWork, artwork_id: int, artist_id):
        async with uow:
            try:
                artist = await uow.artist.get(artist_id)
            except NoResultFound:
                raise ObjectNotFoundException("Художник не найден.")

            try:
                artwork = await uow.artworks.get(artwork_id)
                artwork.artist = artist
                await uow.commit()
                return artwork
            except NoResultFound:
                raise ObjectNotFoundException("Арт-объект не найден.")
