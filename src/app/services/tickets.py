import asyncio
import json
from datetime import datetime
from typing import Optional, List, Union, TypeVar, Type, Annotated

import pydantic
from fastapi import UploadFile, Depends, File, Body
from fastapi_pagination import Params
from pydantic import BaseModel

from app.api.utils.paginator import MyParams
from app.modules import (
    TicketBase,
    ArtworkTicket,
    Moderator,
    ArtworkImage,
    ArtworkLocation,
)
from app.modules.artworks.schemas.artwork import ArtworkCreateSchema
from app.modules.artworks.schemas.artwork_image import ArtworkImageCreateSchema
from app.modules.artworks.schemas.artwork_location import ArtworkLocationCreateSchema
from app.modules.cloud_storage.schemas.image import ImageCreateSchema, ImageReadSchema
from app.modules.tickets.schemas.ticket_artwork import (
    ArtworkTicketCreateSchema,
    ArtworkTicketReadSchema,
    ArtworkTicketUpdateSchema,
)
from app.modules.tickets.schemas.ticket_base import TicketCreateSchema, TicketReadSchema
from app.modules.tickets.utils.classes import (
    TicketModel,
    TicketRegistry,
    TicketStatus,
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
    # location_data = artwork_schema.location
    #
    # artwork_dict = artwork_schema.model_dump(exclude={"location"})
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

    # region Ticket
    @staticmethod
    async def get_ticket(
        uow: UnitOfWork, ticket_id: int, ticket_model: Optional[TicketModel] = None, user_id: int | None = None
    ):
        async with uow:
            if ticket_model:
                ticket = await uow.tickets.get_ticket_by_ticket_model(
                    ticket_id=ticket_id, ticket_model_enum_value=ticket_model, user_id=user_id
                )
            else:
                ticket = await uow.tickets.get_ticket_by_ticket_model(
                    ticket_id=ticket_id, ticket_model_enum_value=TicketModel.TICKET, user_id=user_id
                )
            return ticket

    @staticmethod
    async def get_tickets(
        uow: UnitOfWork,
        pagination: MyParams | None = None,
        ticket_model: TicketModel | None = None,
        user_id: int | None = None
    ):
        """
        Возвращает тикеты, в зависимости от того, какие параметры были переданы.

        :param uow: Нужен для работы с БД.
        :type uow: UnitOfWork

        :param pagination: Отвечает за пагинацию: в последствии достаётся offset и limit для запроса к БД.
        :type pagination: MyParams | None

        :param ticket_model: Нужен для разделения логики получения различных типов тикетов.
        :type uow: TicketModel | None

        :param user_id: Служит для дальнейшей фильтрации тикетов по id пользователя - создателя тикета.
        :type user_id: Int | None
        """
        async with uow:
            # ToDo: Посмотреть: крашнется ли функция, если передать pagination=None
            #  (в таком случае, ведь, не будут инициализированы переменные offset, limit)
            if pagination:
                pagination_raw_params = pagination.to_raw_params()
                offset = pagination_raw_params.offset
                limit = pagination_raw_params.limit

            if ticket_model:
                tickets = await uow.tickets.get_all_tickets(ticket_model_enum_value=ticket_model,
                                                            offset=offset, limit=limit, user_id=user_id)
            else:
                # Возвращаем абсолютно все тикеты
                tickets = await uow.tickets.get_all_tickets(ticket_model_enum_value=TicketModel.TICKET,
                                                            offset=offset, limit=limit, user_id=user_id)

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

    # endregion Ticket

    # region ArtworkTicket

    @staticmethod
    async def create_artwork_ticket(
        uow: UnitOfWork,
        user: User,
        artwork_ticket_schema: ArtworkTicketCreateSchema,
        images: Optional[List[UploadFile]] = None,
        thumbnail_image_index: Optional[int] = None,
    ):
        if not thumbnail_image_index:
            thumbnail_image_index = 0

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
                        "created_at": (
                            image.created_at.isoformat()
                            if hasattr(image, "created_at")
                            and isinstance(image.created_at, datetime)
                            else None
                        ),
                    }
                    for image in ticket_images
                ]

                if location_data:
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

    async def update_artwork_ticket(
        self,
        uow: UnitOfWork,
        user: User,
        artwork_ticket_id: int,
        artwork_ticket_schema: Optional[ArtworkTicketUpdateSchema] = None,
        images: Optional[List[UploadFile]] = None,
        thumbnail_image_index: Optional[int] = None,
    ):
        async with uow:
            # Получаем текущий объект в БД
            artwork_ticket_current: ArtworkTicket = await uow.artwork_tickets.get(
                obj_id=artwork_ticket_id
            )

            if artwork_ticket_current.status != TicketStatus.PENDING:
                raise ValueError(
                    "Нельзя изменить уже подтверждённый или отклонённый запрос"
                )

            cur_artwork_ticket_artwork_data: dict = (
                artwork_ticket_current.artwork_data
                if artwork_ticket_current.artwork_data
                else dict()
            )

            # Обновлённая схема. Исключаем все None (null) и пустые поля
            new_artwork_ticket_data: dict = artwork_ticket_schema.model_dump(
                exclude_none=True, exclude_unset=True
            )
            if hasattr(
                artwork_ticket_schema, "artwork_data"
            ) and cur_artwork_ticket_artwork_data.get("images"):
                ...  # TODO:  Ничего ты не сделал, обманщик!

            # if hasattr(artwork_ticket_schema, "artwork_data"):
            #     new_artwork_ticket_artwork_data: dict = artwork_ticket_schema.artwork_data.model_dump()
            #     cur_artwork_ticket_artwork_data: dict = artwork_ticket_current.artwork_data if artwork_ticket_current.artwork_data else dict()
            #
            #     combined_artwork_tickets_data = cur_artwork_ticket_artwork_data | new_artwork_ticket_artwork_data
            #
            #     try:
            #         artwork_ticket_current_update_schema = ArtworkTicketUpdateSchema(**combined_artwork_tickets_data)
            #     except:
            #         print("Не получилось создать схему из artwork_data.")

            # Редактирование тикета арт-объекта
            artwork_ticket = await uow.artwork_tickets.edit(
                obj_id=artwork_ticket_id, obj_data=new_artwork_ticket_data
            )

            await uow.commit()

            return artwork_ticket

    @staticmethod
    async def approve_artwork_ticket(
        uow: UnitOfWork,
        moderator: Moderator,
        artwork_ticket_id: int,
    ):
        async with uow:
            # Получаем объект ArtworkTicket в БД
            artwork_ticket: ArtworkTicket = await uow.artwork_tickets.get(
                obj_id=artwork_ticket_id
            )

            if artwork_ticket.status == TicketStatus.ACCEPTED:
                raise ValueError("Уже подтверждено")

            # "Присоединяем" модератора к тикету.
            artwork_ticket.moderator_id = moderator.id
            # artwork_ticket.moderator = moderator

            # Из artwork_ticket.artwork_data -> Artwork
            ticket_artwork_data: dict = (
                artwork_ticket.artwork_data
            )  # Тут, по факту, ArtworkCreateSchema,
            # но с доп. полем images. Исправлю в следующем обновлении.

            artwork_location_data = ticket_artwork_data.get("location")
            ticket_artwork_images = ticket_artwork_data.get(
                "images"
            )  # TODO: В схеме не указано! Но оно есть. Переделать.

            # artwork_dict = ticket_artwork_data.model_dump(exclude={"location", "images"})
            ticket_artwork_data.pop("location", None)
            ticket_artwork_data.pop("images", None)

            # Для удобства. Всё равно переделывать.

            artwork_dict = ticket_artwork_data

            artwork_dict["added_by_user_id"] = artwork_ticket.user_id
            artwork_dict["artist_id"] = (
                ticket_artwork_data.get("artist_id")
                if ticket_artwork_data.get("artist_id")
                else None
            )
            artwork_dict["festival_id"] = (
                ticket_artwork_data.get("festival_id")
                if ticket_artwork_data.get("festival_id")
                else None
            )

            # region Создание Арт-объекта из подготовленного словаря
            artwork = await uow.artworks.create(artwork_dict)

            if artwork.artist_id:
                artwork.artist = await uow.artist.get(artwork.artist_id)
            else:
                artwork.artist = None

            artwork_images = list()
            if ticket_artwork_images is not None:
                for image in ticket_artwork_images:
                    image = await uow.images.filter(image_url=image.get("image_url"))
                    image = image[0]
                    artwork_image_schema = ArtworkImageCreateSchema(
                        artwork_id=artwork.id,
                        image_url=image.image_url,
                        public_key=image.public_key,
                        file_path=image.file_path,
                    )

                    # image.__class__ = ArtworkImage
                    # image.discriminator = "artwork_image"
                    # image.artwork_id = artwork.id
                    # image.artwork = artwork

                    # TODO: Под вопросом...
                    # artwork_image = image
                    # artwork_image.__class__ = ArtworkImage
                    #
                    # artwork_image.discriminator = "artwork_image"

                    artwork_image = await uow.artwork_images.create(
                        artwork_image_schema
                    )
                    artwork_images.append(artwork_image)

                artwork.images = artwork_images

            if artwork_location_data is not None:
                artwork_location_schema = ArtworkLocationCreateSchema(
                    artwork_id=artwork.id,
                    latitude=artwork_location_data.get("latitude"),
                    longitude=artwork_location_data.get("longitude"),
                    address=artwork_location_data.get("address"),
                )

                artwork_location: ArtworkLocation = await uow.artwork_locations.create(
                    artwork_location_schema
                )

                thumbnail_image = artwork_location_data.get("thumbnail_image")  # url
                if thumbnail_image is not None:
                    exist_image = await uow.artwork_images.filter(
                        image_url=thumbnail_image
                    )
                    if exist_image:
                        artwork_location.thumbnail_image_id = exist_image[0].id
                        artwork_location.thumbnail_image = exist_image[0]

            # Добавляем artwork.id к ArtworkTicket
            artwork_ticket.artwork_id = artwork.id
            # Изменяем статус заявки
            artwork_ticket.status = TicketStatus.ACCEPTED
            # endregion
            await uow.session.flush()
            await uow.session.refresh(artwork_ticket)
            await uow.commit()
            return artwork_ticket

    @staticmethod
    async def reject_artwork_ticket(
        uow: UnitOfWork, moderator: Moderator, artwork_ticket_id: int
    ):
        async with uow:
            # Получаем объект ArtworkTicket в БД
            artwork_ticket: ArtworkTicket = await uow.artwork_tickets.get(
                obj_id=artwork_ticket_id
            )

            if artwork_ticket.status != TicketStatus.PENDING:
                raise ValueError("Тикет не в статусе ожидания")

            artwork_ticket.status = TicketStatus.REJECTED

            # "Присоединяем" модератора к тикету.
            artwork_ticket.moderator_id = moderator.id
            # artwork_ticket.moderator = moderator

            await uow.session.flush()
            await uow.session.refresh(artwork_ticket)
            await uow.commit()
            return artwork_ticket

    # endregion ArtworkTicket

    @staticmethod
    async def delete_all_tickets(uow: UnitOfWork):
        async with uow:
            await uow.tickets.delete_all()

    @staticmethod
    async def get_all_tickets(
        uow: UnitOfWork,
        ticket_model: TicketModel | None = None,
        user_id: int | None = None
    ):
        async with uow:
            if ticket_model:
                tickets = await uow.tickets.get_all_tickets(ticket_model_enum_value=ticket_model,
                                                            user_id=user_id)
            else:
                tickets = await uow.tickets.get_all()

            return tickets

    @staticmethod
    async def count(
        uow: UnitOfWork,
        # ticket_model: Optional[TicketModel] = None,
    ) -> int:
        async with uow:
            # if ticket_model:
            #     tickets = await uow.tickets.get_all_tickets_by_ticket_model(
            #         ticket_model_enum_value=ticket_model
            #     )
            # else:
            #     tickets = await uow.tickets.get_all()

            return await uow.tickets.count()
