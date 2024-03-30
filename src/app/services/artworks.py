import asyncio
from typing import Optional, List

from fastapi import UploadFile, HTTPException
from sqlalchemy.exc import NoResultFound
from starlette import status

from app.api.utils.libs.fastapi_filter.contrib.sqlalchemy import Filter
from fastapi_pagination import Params

from app.modules import Moderator
from app.modules.artworks.models.artwork import Artwork
from app.modules.artworks.models.artwork_moderation import ArtworkModerationStatus
from app.modules.artworks.schemas.artwork import (
    ArtworkCreateSchema,
    ArtworkUpdateSchema,
)
from app.modules.artworks.schemas.artwork_image import ArtworkImageCreateSchema
from app.modules.artworks.schemas.artwork_location import ArtworkLocationCreateSchema
from app.modules.artworks.schemas.artwork_moderation import (
    ArtworkModerationCreateSchema,
)
from app.modules.users.models import User
from app.services.cloud_storage import CloudStorageService
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
        if not thumbnail_image_index:
            thumbnail_image_index = 0

        location_data = artwork_schema.location

        artwork_dict = artwork_schema.model_dump(exclude={"location"})

        artwork_dict["added_by_user_id"] = moderator.user_id
        artwork_dict["artist_id"] = (
            artwork_schema.artist_id if artwork_schema.artist_id else None
        )
        artwork_dict["festival_id"] = (
            artwork_schema.festival_id if artwork_schema.festival_id else None
        )
        if artwork_schema.links:
            artwork_dict["links"] = [i.__str__() for i in artwork_schema.links]

        async with uow:
            artwork = await uow.artworks.create(artwork_dict)

            # Добавление связи ArtworkModeration
            artwork.moderation = await uow.artwork_moderation.create(
                ArtworkModerationCreateSchema(artwork_id=artwork.id)
            )

            # Добавление связи ArtworkLocation
            artwork.location = await uow.artwork_locations.create(
                ArtworkLocationCreateSchema(
                    **location_data.model_dump(), artwork_id=artwork.id
                )
            )

            if images or images_urls:
                images_data_list = list()
                artwork_images = list()
                unique_image_urls = set()

                # Создаем список корутин, каждая из которых отвечает за загрузку и обработку одного изображения
                async def process_image(
                    image: Optional[UploadFile] = None, image_url: Optional[str] = None
                ):
                    if image:
                        cloud_file = await CloudStorageService.upload_to_yandex_disk(
                            image=image
                        )
                    elif image_url:
                        cloud_file = (
                            await CloudStorageService.upload_to_yandex_disk_by_url(
                                image_url=image_url
                            )
                        )

                    # ToDo: Добавлять созданную схему во все схемы, для дальнейшего создания объектов одним запросом к
                    #  БД. создать create_many

                    # Создание объекта Pydantic
                    image_create = ArtworkImageCreateSchema(
                        image_url=cloud_file.public_url,
                        public_key=cloud_file.public_key,
                        file_path=cloud_file.file_path,
                        artwork_id=artwork.id,
                    )

                    # Проверка отсутствия image_url в уникальных
                    if image_create.image_url not in unique_image_urls:
                        unique_image_urls.add(image_create.image_url)
                        images_data_list.append(image_create)

                # Запускаем корутины асинхронно
                await asyncio.gather(*[process_image(image=image) for image in images])

                await asyncio.gather(
                    *[process_image(image_url=image_url) for image_url in images_urls]
                )

                await asyncio.gather(
                    *[process_image(image_url=image_url) for image_url in images_urls]
                )

                # Добавление в базу данных
                for image_data in images_data_list:
                    exist_image = await uow.artwork_images.filter(
                        image_url=image_data.image_url
                    )
                    if exist_image:
                        artwork_images.append(exist_image[0])
                    else:
                        artwork_images.append(
                            await uow.artwork_images.create(image_data)
                        )

                # Привязка Artwork к ArtworkImage
                artwork.images = artwork_images

                if location_data:
                    if 0 <= thumbnail_image_index < len(artwork_images):
                        img = artwork_images[thumbnail_image_index]
                        # img.generate_thumbnail_url()
                        artwork.location.thumbnail_image = img

            if artwork.artist_id:
                artwork.artist = await uow.artist.get(artwork.artist_id)
            else:
                artwork.artist = None
            await uow.commit()
            return artwork

    @staticmethod
    async def get_artworks_by_moderation_status(
        uow: UnitOfWork,
        pagination: Optional[Params] = None,
        filters: Optional[Filter] = None,
        **filter_by
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
        pagination: Optional[Params] = None,
        filters: Optional[Filter] = None,
    ) -> list[Artwork]:
        filters.add_filtering_fields(moderation__status=ArtworkModerationStatus.PENDING)
        return await self.get_artworks_by_moderation_status(
            uow=uow, pagination=pagination, filters=filters
        )

    async def get_approved_artworks(
        self,
        uow: UnitOfWork,
        pagination: Optional[Params] = None,
        filters: Optional[Filter] = None,
        **filter_by
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
        pagination: Optional[Params] = None,
        filters: Optional[Filter] = None,
    ) -> list[Artwork]:
        filters.add_filtering_fields(
            moderation__status=ArtworkModerationStatus.REJECTED
        )

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
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artwork not found")

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
                await uow.artwork_moderation.edit(
                    artwork.moderation.id, moderation_dict
                )

            await uow.commit()

            return artwork

    async def delete_artwork(self, uow: UnitOfWork, artwork_id: int):
        async with uow:
            artwork = await self.get_artwork(uow=uow, artwork_id=artwork_id)

            artwork_ticket = await uow.artwork_tickets.filter(artwork_id=artwork.id)
            artwork_ticket = artwork_ticket[0]

            artwork_ticket.artwork_id = None

            artwork_images = artwork.images
            for img in artwork_images:
                # ToDo: Переделать фильтр
                exist_image = await uow.artworks.filter(
                    images={uow.artwork_images.model.image_url: img.image_url}
                )
                if len(exist_image) > 1:
                    continue
                else:
                    await CloudStorageService.delete_from_yandex_disk(img.image_url)

            await uow.artworks.delete(artwork_id)
            await uow.commit()
