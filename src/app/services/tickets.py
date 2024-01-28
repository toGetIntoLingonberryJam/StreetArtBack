import asyncio
from typing import Optional, List, Union, TypeVar, Type, Annotated

import pydantic
from fastapi import UploadFile, Depends, File, Body
from fastapi_pagination import Params

from app.api.utils.paginator import MyParams
from app.modules import TicketBase, ArtworkTicket
from app.modules.cloud_storage.schemas.image import ImageCreateSchema, ImageReadSchema
from app.modules.tickets.schemas.ticket_artwork import (
    ArtworkTicketCreateSchema,
    ArtworkTicketReadSchema,
)
from app.modules.tickets.schemas.ticket_base import TicketCreateSchema, TicketReadSchema
from app.modules.tickets.utils.classes import (
    TicketModel,
    TicketRegistry,
)
from app.modules.tickets.utils.types import (
    TicketCreateSchemaType,
)
from app.modules.users.models import User
from app.services.cloud_storage import CloudStorageService
from app.utils.unit_of_work import UnitOfWork


class TicketsService:
    # @staticmethod
    # async def create_artwork_ticket(
    #     uow: UnitOfWork,
    #     user: User,
    #     artwork_ticket_schem: ArtworkTicketCreateSchema,
    #     images: Optional[List[UploadFile]] = None,
    #     thumbnail_image_index: Optional[int] = None,
    # ):
    #     pass
    # location_data = artwork_schem.location
    #
    # artwork_dict = artwork_schem.model_dump(exclude={"location"})
    #
    # artwork_dict["added_by_user_id"] = user.id
    #
    # async with uow:
    #     artwork = await uow.artworks.create(artwork_dict)
    #
    #     # Добавление связи ArtworkModeration
    #     artwork.moderation = await uow.artwork_moderation.create(
    #         ArtworkModerationCreateSchema(artwork_id=artwork.id)
    #     )
    #
    #     # Добавление связи ArtworkLocation
    #     artwork.location = await uow.artwork_locations.create(
    #         ArtworkLocationCreateSchema(
    #             **location_data.model_dump(), artwork_id=artwork.id
    #         )
    #     )
    #
    #     if images:
    #         images_data_list = list()
    #         artwork_images = list()
    #         unique_image_urls = set()
    #
    #         # Создаем список корутин, каждая из которых отвечает за загрузку и обработку одного изображения
    #         async def process_image(image):
    #             public_image_url = await upload_to_yandex_disk(image=image)
    #
    #             img_data = {
    #                 "image_url": public_image_url,
    #                 "artwork_id": artwork.id,
    #             }
    #
    #             # ToDo: Добавлять созданную схему во все схемы, для дальнейшего создания объектов одним запросом к
    #             #  БД. создать create_many
    #             # Создание объекта Pydantic
    #             image_create = ArtworkImageCreateSchema(**img_data)
    #
    #             # Проверка отсутствия image_url в уникальных
    #             if image_create.image_url not in unique_image_urls:
    #                 unique_image_urls.add(image_create.image_url)
    #                 images_data_list.append(image_create)
    #
    #         # Запускаем корутины асинхронно
    #         await asyncio.gather(*[process_image(image) for image in images])
    #
    #         # Добавление в базу данных
    #         for image_data in images_data_list:
    #             exist_image = await uow.artwork_images.filter(
    #                 image_url=image_data.image_url
    #             )
    #             if exist_image:
    #                 artwork_images.append(exist_image[0])
    #             else:
    #                 artwork_images.append(
    #                     await uow.artwork_images.create(image_data)
    #                 )
    #
    #         # Привязка Artwork к ArtworkImage
    #         artwork.images = artwork_images
    #
    #         if location_data:
    #             if thumbnail_image_index:
    #                 if 0 <= thumbnail_image_index < len(artwork_images):
    #                     img = artwork_images[thumbnail_image_index]
    #                     # img.generate_thumbnail_url()
    #                     artwork.location.thumbnail_image = img
    #
    #     await uow.commit()
    #     return artwork

    @staticmethod
    async def approve_artwork_ticket():
        pass

    @staticmethod
    async def reject_artwork_ticket():
        pass

    @staticmethod
    async def get_ticket(
        uow: UnitOfWork, ticket_id: int, ticket_model: Optional[TicketModel] = None
    ):
        async with uow:
            if ticket_model:
                ticket = await uow.tickets.get_ticket_by_ticket_model(
                    ticket_id=ticket_id, ticket_model_enum_value=ticket_model
                )
            else:
                ticket = await uow.tickets.get(obj_id=ticket_id)
            return ticket

    @staticmethod
    async def get_tickets(
        uow: UnitOfWork,
        pagination: Optional[Params] = None,
        ticket_model: Optional[TicketModel] = None,
    ):
        async with uow:
            if pagination:
                pagination_raw_params = pagination.to_raw_params()
                offset = pagination_raw_params.offset
                limit = pagination_raw_params.limit

            if ticket_model:
                tickets = await uow.tickets.get_all_tickets_by_ticket_model(
                    ticket_model_enum_value=ticket_model, offset=offset, limit=limit
                )
            else:
                tickets = await uow.tickets.get_all(offset=offset, limit=limit)

            return tickets

    @staticmethod
    async def create_ticket(
        uow: UnitOfWork,
        user: User,
        ticket_schema: TicketCreateSchema,
    ):
        async with uow:
            ticket_data = ticket_schema.model_dump()
            ticket_data["user_id"] = user.id

            # ticket = await uow.tickets.create_ticket_by_ticket_model(
            #     user=user, ticket_model_enum_value=ticket_model, ticket_data=ticket_schema
            # )

            ticket = await uow.tickets.create(obj_data=ticket_data)

            await uow.commit()
            return ticket

    @staticmethod
    async def create_artwork_ticket(
        uow: UnitOfWork,
        user: User,
        artwork_ticket_schema: ArtworkTicketCreateSchema,
        images: Optional[List[UploadFile]] = None,
        thumbnail_image_index: Optional[int] = None,
    ):
        async with uow:
            location_data = artwork_ticket_schema.artwork_data.location

            ticket_data = artwork_ticket_schema.model_dump()
            # ticket_data = artwork_ticket_schema.model_dump(exclude={"location"})
            ticket_data["user_id"] = user.id

            if images:
                images_data_list = list()
                ticket_images = list()
                unique_image_urls = set()

                # Создаем список корутин, каждая из которых отвечает за загрузку и обработку одного изображения
                async def process_image(image):
                    cloud_file = await CloudStorageService.upload_to_yandex_disk(
                        image=image
                    )

                    # ToDo: Добавлять созданную схему во все схемы, для дальнейшего создания объектов одним запросом к
                    #  БД. создать create_many

                    # Создание объекта Pydantic
                    image_create = ImageCreateSchema(
                        image_url=cloud_file.public_url,
                        public_key=cloud_file.public_key,
                        file_path=cloud_file.file_path,
                    )

                    # Проверка отсутствия image_url в уникальных
                    if image_create.image_url not in unique_image_urls:
                        unique_image_urls.add(image_create.image_url)
                        images_data_list.append(image_create)

                # Запускаем корутины асинхронно
                await asyncio.gather(*[process_image(image) for image in images])

                # Добавление в базу данных
                for image_data in images_data_list:
                    exist_image = await uow.images.filter(
                        image_url=image_data.image_url
                    )
                    if exist_image:
                        ticket_images.append(exist_image[0])
                    else:
                        ticket_images.append(await uow.images.create(image_data))

                ticket_data["artwork_data"]["images"] = [
                    # ImageReadSchema(**image.__dict__).model_dump()
                    # ImageReadSchema(**image.__dict__).__dict__
                    # for image in ticket_images
                    {
                        **ImageReadSchema(**image.__dict__).__dict__,
                        "created_at": image.created_at.isoformat()
                        if hasattr(image, "created_at")
                        and isinstance(image.created_at, datetime)
                        else None,
                    }
                    for image in ticket_images
                ]

                if location_data:
                    if thumbnail_image_index:
                        if 0 <= thumbnail_image_index < len(ticket_images):
                            img = ticket_images[thumbnail_image_index]
                            # img.generate_thumbnail_url()
                            ticket_data["artwork_data"]["location"][
                                "thumbnail_image"
                            ] = img.image_url

            # ticket = await uow.tickets.create_ticket_by_ticket_model(
            #     user=user, ticket_model_enum_value=ticket_model, ticket_data=ticket_schema
            # )

            # ticket = await uow.tickets.create(obj_data=ticket_data)

            artwork_ticket = await uow.artwork_tickets.create(ticket_data)

            await uow.commit()
            return artwork_ticket
