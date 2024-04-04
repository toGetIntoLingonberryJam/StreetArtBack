from app.db import async_session_maker
from app.repos.artworks import (
    ArtworkRepository,
    ArtworkLocationRepository,
    ArtworkImageRepository,
    ArtworkModerationRepository,
    FestivalRepository,
)
from app.repos.tickets import TicketBaseRepository, ArtworkTicketRepository
from app.repos.cloud_storage import ImageRepository
from app.repos.users import (
    ModeratorRepository,
    ArtistRepository,
    UsersRepository,
)

from app.repos.collection import (
    ArtworkLikeRepository,
    ArtistLikeRepository,
    FestivalLikeRepository,
)


class UnitOfWork:
    def __init__(self):
        self.session_factory = async_session_maker
        self._nested = 0

    async def __aenter__(self):
        if self._nested == 0:
            self.session = self.session_factory()
            await self._initialize_resources()
        self._nested += 1
        return self
        # self.tasks = TasksRepository(self.session)
        # self.task_history = TaskHistoryRepository(self.session)

    async def __aexit__(self, *args):
        # await self.rollback()
        self._nested -= 1
        if self._nested == 0:
            await self.session.close()

    async def _initialize_resources(self):
        self.users = UsersRepository(self.session)
        self.moderator = ModeratorRepository(self.session)
        self.artist = ArtistRepository(self.session)

        self.artworks = ArtworkRepository(self.session)
        self.artwork_locations = ArtworkLocationRepository(self.session)
        self.artwork_images = ArtworkImageRepository(self.session)
        self.images = ImageRepository(self.session)
        self.artwork_moderation = ArtworkModerationRepository(self.session)
        self.tickets = TicketBaseRepository(self.session)
        self.artwork_tickets = ArtworkTicketRepository(self.session)
        self.festival = FestivalRepository(self.session)

        self.artwork_like = ArtworkLikeRepository(self.session)
        self.artist_like = ArtistLikeRepository(self.session)
        self.festival_like = FestivalLikeRepository(self.session)

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
