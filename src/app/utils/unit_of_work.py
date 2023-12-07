from app.db import async_session_maker
from app.repos.artworks import ArtworkRepository, ArtworkLocationRepository, ArtworkImageRepository, \
    ArtworkModerationRepository
from app.repos.users import ReactionRepository, ModeratorRepository, ArtistRepository


class UnitOfWork:
    def __init__(self):
        self.session_factory = async_session_maker

    async def __aenter__(self):
        self.session = self.session_factory()

        self.users = ReactionRepository(self.session)
        self.moderator = ModeratorRepository(self.session)
        self.artist = ArtistRepository(self.session)

        self.artworks = ArtworkRepository(self.session)
        self.artwork_locations = ArtworkLocationRepository(self.session)
        self.artwork_images = ArtworkImageRepository(self.session)
        self.artwork_moderation = ArtworkModerationRepository(self.session)
        self.reaction = ReactionRepository(self.session)
        # self.tasks = TasksRepository(self.session)
        # self.task_history = TaskHistoryRepository(self.session)

    async def __aexit__(self, *args):
        # await self.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()