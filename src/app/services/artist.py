from app.modules.artists.models import Artist
from app.modules.artists.schemas import ArtistCreate
from app.utils.exceptions import UserNotFoundException, IncorrectInput
from app.utils.unit_of_work import UnitOfWork


class ArtistsService:
    async def get_artist_by_id(self, uow: UnitOfWork, artist_id: int):
        async with uow:
            artist = await uow.artist.get(artist_id)
            return artist

    async def create_artist(self, uow: UnitOfWork, artist_schema: ArtistCreate):
        async with uow:
            artist = Artist()
            artist.name = artist_schema.name
            if artist_schema.user_id:
                user = uow.users.get(artist_schema.user_id)
                if not user:
                    raise UserNotFoundException("Пользователь не найден.")
                elif not user.is_verified:
                    raise IncorrectInput("Пользователь не верифициован.")
                else:
                    artist.user_id = artist_schema.user_id
            artist = await uow.artist.create(artist)
            await uow.commit()
            return artist

    async def get_all_artist(self, uow: UnitOfWork, offset: int = 0, limit: int = None):
        async with uow:
            artists = await uow.artist.get_all(offset, limit)
            return artists

    async def delete_artist(self, uow: UnitOfWork, artist_id: int):
        async with uow:
            await uow.artist.delete(artist_id)

    async def get_artist_by_user_id(self, uow: UnitOfWork, user_id: int):
        async with uow:
            artist = uow.artist.filter(user_id=user_id)
            return artist
