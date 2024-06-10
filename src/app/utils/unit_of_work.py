from typing import Type

from sqlalchemy.orm import DeclarativeMeta

from app.db import async_session_maker
from app.repos.artworks import (
    ArtworkLocationRepository,
    ArtworkRepository,
    FestivalRepository,
)
from app.repos.collection import (
    ArtistLikeRepository,
    ArtworkLikeRepository,
    FestivalLikeRepository,
)
from app.repos.images import (
    ImageArtworkRepository,
    ImageRepository,
    ImageTicketRepository,
)
from app.repos.SQLAlchemy_repository import SQLAlchemyRepository
from app.repos.tickets import TicketArtworkRepository, TicketBaseRepository
from app.repos.users import ArtistRepository, ModeratorRepository, UsersRepository


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
        self.images_artwork = ImageArtworkRepository(self.session)
        self.images_ticket = ImageTicketRepository(self.session)
        self.images = ImageRepository(self.session)
        self.tickets = TicketBaseRepository(self.session)
        self.tickets_artwork = TicketArtworkRepository(self.session)
        self.festival = FestivalRepository(self.session)

        self.artwork_like = ArtworkLikeRepository(self.session)
        self.artist_like = ArtistLikeRepository(self.session)
        self.festival_like = FestivalLikeRepository(self.session)

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()

    @classmethod
    async def get_repo_by_class(
        cls, model_class: DeclarativeMeta
    ) -> SQLAlchemyRepository:
        async with cls() as uow:
            for attr_name in dir(uow):
                attr = getattr(uow, attr_name)
                if isinstance(attr, SQLAlchemyRepository) and attr.model == model_class:
                    return attr
            raise ValueError("Repository for the given model class not found")
