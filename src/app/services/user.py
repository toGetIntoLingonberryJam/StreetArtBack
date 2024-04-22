from app.modules.collections.models import LikeType
from app.services.artist import ArtistsService
from app.services.artworks import ArtworksService
from app.services.festival import FestivalService
from app.utils.unit_of_work import UnitOfWork


class UserService:
    async def get_artwork_likes(self, uow: UnitOfWork, user_id: int):
        likes = await self.get_user_likes(uow, user_id, LikeType.ARTWORK)
        artworks = [
            (await ArtworksService().get_artwork(uow, like.artwork_id))
            for like in likes
        ]
        return artworks

    async def get_artist_likes(self, uow: UnitOfWork, user_id: int):
        likes = await self.get_user_likes(uow, user_id, LikeType.ARTIST)
        artists = [
            (await ArtistsService().get_artist_by_id(uow, like.artist_id))
            for like in likes
        ]
        return artists

    async def get_festival_likes(self, uow: UnitOfWork, user_id: int):
        likes = await self.get_user_likes(uow, user_id, LikeType.FESTIVAL)
        festivals = [
            (await FestivalService().get_festival_by_id(uow, like.festival_id))
            for like in likes
        ]
        return festivals

    @staticmethod
    async def get_user_likes(uow: UnitOfWork, user_id: int, like_type: LikeType):
        async with uow:
            if like_type == LikeType.ARTIST:
                likes = await uow.artist_like.filter(user_id=user_id)
            elif like_type == LikeType.ARTWORK:
                likes = await uow.artwork_like.filter(user_id=user_id)
            elif like_type == LikeType.FESTIVAL:
                likes = await uow.festival_like.filter(user_id=user_id)
            return likes

    async def edit_user_settings(self, uow: UnitOfWork, user_id: int, **kwargs):
        async with uow:
            user = await uow.users.edit(user_id, kwargs)
            return user

    async def get_user_status_like(self,
                                   uow: UnitOfWork,
                                   user_id: int,
                                   like_type: LikeType,
                                   object_id: int) -> bool:
        async with uow:
            if like_type == LikeType.ARTIST:
                like = await uow.artist_like.get(user_id=user_id, artist_id=object_id)
            elif like_type == LikeType.ARTWORK:
                like = await uow.artwork_like.get(user_id=user_id, artwork_id=object_id)
            elif like_type == LikeType.FESTIVAL:
                like = await uow.festival_like.get(user_id=user_id, festival_id=object_id)
            return like is not None
