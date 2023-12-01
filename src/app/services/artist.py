from app.utils.unit_of_work import UnitOfWork


class ArtistsService:
    async def get_artist(self, uow: UnitOfWork, artist_id: int):
        async with uow:
            artist = await uow.artist.get(artist_id)
            return artist
