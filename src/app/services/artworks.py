import asyncio
from typing import List, Optional

from fastapi import UploadFile, HTTPException
from starlette import status

from app.api.utils.libs.fastapi_filter.contrib.sqlalchemy import Filter
from app.api.utils.paginator import MyParams
from app.db import get_async_session
from app.modules.artworks.models.artwork import Artwork
from app.modules.artworks.models.artwork_moderation import ArtworkModerationStatus
from app.modules.artworks.schemas.artwork import ArtworkCreateSchema, ArtworkUpdateSchema
from app.modules.artworks.schemas.artwork_location import ArtworkLocationCreateSchema
from app.modules.artworks.schemas.artwork_moderation import ArtworkModerationCreateSchema
from app.modules.images.schemas.image_artwork import ImageArtworkCreateSchema
from app.modules.models import Moderator
from app.modules.tickets.schemas.ticket_artwork import TicketArtworkCreateSchema
from app.modules.users.manager import get_user_manager
from app.modules.users.models import get_user_db
from app.services.cloud_storage import CloudStorageService
from app.services.tickets import TicketsService
from app.utils.exceptions import ObjectNotFoundException

# from app.utils.cloud_storage_config import (
#     upload_to_yandex_disk,
#     delete_from_yandex_disk,
# )
from app.utils.unit_of_work import UnitOfWork


class ArtworksService:
    @staticmethod
    async def create_artwork(
        uow: UnitOfWork,
        moderator: Moderator,
        artwork_schema: ArtworkCreateSchema,
        images: Optional[List[UploadFile]] = None,
        images_urls: Optional[List[str]] = None,
        thumbnail_image_index: Optional[int] = None,
    ):
        """
        Создает объект Artwork, используя методы создания и подтверждения тикета.

        :param uow: UnitOfWork
        :param moderator: Модератор, создающий арт-объект
        :param artwork_schema: Данные для создания арт-объекта
        :param images: Список загружаемых изображений
        :param images_urls: Список URL-адресов изображений
        :param thumbnail_image_index: Индекс изображения для миниатюры
        :return: Созданный объект Artwork
        """
        async with uow:
            user_manager = [item async for item in get_user_manager()][0]
            user_manager.user_db = [item async for item in get_user_db()][0]
            user_manager.user_db.session = uow.session
            user = await user_manager.get(moderator.user_id)

            # Создание тикета на основе предоставленных данных
            ticket_artwork_schema = TicketArtworkCreateSchema(artwork_data=artwork_schema)
            ticket_artwork = await TicketsService.create_ticket_artwork(
                uow,
                user,
                ticket_artwork_schema,
                images,
                images_urls,
                thumbnail_image_index,
            )

            # Подтверждение тикета для создания объекта Artwork
            approved_ticket_artwork = await TicketsService.approve_ticket_artwork(
                uow,
                moderator,
                "Создано напрямую через ArtworkService.create_artwork",
                ticket_artwork.id,
            )

            # Получение созданного объекта Artwork из подтвержденного тикета
            artwork = await uow.artworks.get(obj_id=approved_ticket_artwork.object_id)

            return artwork

    @staticmethod
    async def get_artworks_by_moderation_status(
        uow: UnitOfWork,
        pagination: Optional[MyParams] = None,
        filters: Optional[Filter] = None,
        **filter_by,
    ) -> list[Artwork]:
        async with uow:
            offset: int = 0
            limit: Optional[int] = None

            if pagination:
                pagination_raw_params = pagination.to_raw_params()
                offset = pagination_raw_params.offset
                limit = pagination_raw_params.limit

            artworks = await uow.artworks.filter(
                offset=offset, limit=limit, filters=filters, **filter_by
            )
            return artworks

    async def get_pending_artworks(
        self,
        uow: UnitOfWork,
        pagination: Optional[MyParams] = None,
        filters: Optional[Filter] = None,
    ) -> list[Artwork]:
        filters.add_filtering_fields(moderation__status=ArtworkModerationStatus.PENDING)
        return await self.get_artworks_by_moderation_status(
            uow=uow, pagination=pagination, filters=filters
        )

    async def get_approved_artworks(
        self,
        uow: UnitOfWork,
        pagination: Optional[MyParams] = None,
        filters: Optional[Filter] = None,
        **filter_by,
    ) -> list[Artwork]:
        # filters.add_filtering_field(artwork_moderation__status='approved')
        # filters.add_searching_field("artwork_moderation__status")
        # filters.add_ordering_field("artwork_moderation__status")
        if filters:
            filters.add_filtering_fields(
                moderation__status=ArtworkModerationStatus.APPROVED,
            )

        return await self.get_artworks_by_moderation_status(
            uow=uow, pagination=pagination, filters=filters, **filter_by
        )

    async def get_rejected_artworks(
        self,
        uow: UnitOfWork,
        pagination: Optional[MyParams] = None,
        filters: Optional[Filter] = None,
    ) -> list[Artwork]:
        if filters is None:
            filters = Filter()

        filters.add_filtering_fields(moderation__status=ArtworkModerationStatus.REJECTED)

        return await self.get_artworks_by_moderation_status(
            uow=uow, pagination=pagination, filters=filters
        )

    @staticmethod
    async def get_artwork(
        uow: UnitOfWork, artwork_id: int, filters: Filter | None = None, **filter_by
    ):
        try:
            async with uow:
                artwork = await uow.artworks.get(
                    obj_id=artwork_id, filters=filters, **filter_by
                )
                return artwork
        except ObjectNotFoundException:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Artwork not found"
            )

    @staticmethod
    async def get_artworks(uow: UnitOfWork, filters: Filter | None = None, **filter_by):
        async with uow:
            artworks = await uow.artworks.filter(filters=filters, **filter_by)
            return artworks

    @staticmethod
    async def get_all_artworks(uow: UnitOfWork):
        async with uow:
            artworks = await uow.artworks.get_all()
            return artworks

    @staticmethod
    async def get_locations_approved_artworks(
        uow: UnitOfWork, filters: Optional[Filter] = None
    ):
        async with uow:
            filters.add_filtering_fields(
                artwork__moderation__status=ArtworkModerationStatus.APPROVED
            )

            locations = await uow.artwork_locations.filter(filters=filters)

            return locations

    @staticmethod
    async def get_artworks_locations(
        uow: UnitOfWork,
        filters: Optional[Filter] = None,
    ):
        async with uow:
            locations = await uow.artwork_locations.filter(filters=filters)

            return locations

    @staticmethod
    async def update_artwork(
        uow: UnitOfWork, artwork_id: int, artwork_schema: ArtworkUpdateSchema
    ):
        location_dict = (
            artwork_schema.location.model_dump(exclude_unset=True)
            if artwork_schema.location
            else None
        )
        moderation_dict = (
            artwork_schema.moderation.model_dump(exclude_unset=True)
            if artwork_schema.moderation
            else None
        )

        artwork_dict = artwork_schema.model_dump(
            exclude_unset=True, exclude={"location", "moderation"}
        )

        async with uow:
            # Редактирование арт-объекта
            artwork = await uow.artworks.edit(artwork_id, artwork_dict)

            if location_dict:
                # Редактирование локации арт-объекта
                await uow.artwork_locations.edit(artwork.location.id, location_dict)

            if moderation_dict:
                # Редактирование модерации арт-объекта
                await uow.artwork_moderation.edit(artwork.moderation.id, moderation_dict)

            await uow.commit()

            return artwork

    async def delete_artwork(self, uow: UnitOfWork, artwork_id: int):
        async with uow:
            artwork = await self.get_artwork(uow=uow, artwork_id=artwork_id)

            ticket_artwork = await uow.ticket_artworks.filter(artwork_id=artwork.id)
            ticket_artwork = ticket_artwork[0]

            ticket_artwork.artwork_id = None

            image_artworks = artwork.images
            for img in image_artworks:
                # ToDo: Переделать фильтр
                exist_image = await uow.artworks.filter(
                    images={uow.image_artworks.model.image_url: img.image_url}
                )
                if len(exist_image) > 1:
                    continue
                else:
                    await CloudStorageService.delete_from_yandex_disk(img.image_url)

            await uow.artworks.delete(artwork_id)
            await uow.commit()
