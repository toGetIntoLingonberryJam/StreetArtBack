from app.utils.unit_of_work import UnitOfWork


class CollectionService:
    @staticmethod
    async def toggle_artwork_like(uow: UnitOfWork, user_id: int, artwork_id: int) -> bool:
        """Создает реакцию на Artwork. При наличии реацкии на данный Artwork - удаляет реакцию."""
        async with uow:
            current_like = await uow.artwork_like.filter(
                user_id=user_id, artwork_id=artwork_id
            )
            if current_like:
                like = current_like[0]
                await uow.artwork_like.delete(like.id)
            else:
                like = {"user_id": user_id, "artwork_id": artwork_id}
                await uow.artwork_like.create(like)
            await uow.commit()
            return False if current_like else True

    @staticmethod
    async def toggle_artist_like(uow: UnitOfWork, user_id: int, artist_id: int) -> bool:
        """Создает реакцию на Artist. При наличии реацкии на данный Artist - удаляет реакцию."""
        async with uow:
            current_like = await uow.artist_like.filter(
                user_id=user_id, artist_id=artist_id
            )
            if current_like:
                like = current_like[0]
                await uow.artist_like.delete(like.id)
            else:
                like = {"user_id": user_id, "artist_id": artist_id}
                await uow.artist_like.create(like)
            await uow.commit()
            return False if current_like else True

    @staticmethod
    async def toggle_festival_like(
        uow: UnitOfWork, user_id: int, festival_id: int
    ) -> bool:
        """Создает реакцию на Festival. При наличии реацкии на данный Festival - удаляет реакцию."""
        async with uow:
            current_like = await uow.festival_like.filter(
                user_id=user_id, festival_id=festival_id
            )
            if current_like:
                like = current_like[0]
                await uow.festival_like.delete(like.id)
            else:
                like = {"user_id": user_id, "festival_id": festival_id}
                await uow.festival_like.create(like)
            await uow.commit()
            return False if current_like else True
