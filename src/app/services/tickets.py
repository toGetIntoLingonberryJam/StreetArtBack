from typing import List, Optional, Type

from fastapi import UploadFile
from fastapi_pagination import Params

from app.modules.artworks.schemas.artwork import ArtworkCreateSchema
from app.modules.artworks.schemas.artwork_location import (
    ArtworkLocationTicketCreateSchema,
)
from app.modules.images.models import ImageArtwork, ImageTicket
from app.modules.images.schemas.image_artwork import ImageArtworkCreateSchema
from app.modules.images.schemas.image_ticket import ImageTicketCreateSchema
from app.modules.models import ArtworkLocation, Moderator
from app.modules.tickets.models import TicketBase, TicketArtwork
from app.modules.tickets.schemas.ticket_artwork import TicketArtworkCreateSchema
from app.modules.tickets.schemas.ticket_base import TicketCreateSchema
from app.modules.tickets.utils.classes import (
    TicketAvailableObjectClasses,
    TicketModel,
    TicketStatus,
    TicketType,
)
from app.modules.users.models import User
from app.services.artist import ArtistsService
from app.services.cloud_storage import CloudFile, CloudStorageService
from app.utils.exceptions import ObjectNotFoundException
from app.utils.unit_of_work import UnitOfWork


class TicketsService:
    # region Ticket
    @staticmethod
    async def get_ticket(
        uow: UnitOfWork,
        ticket_id: int,
        ticket_model: Optional[TicketModel] = None,
        user_id: int | None = None,
    ):
        async with uow:
            ticket: Type[TicketBase] = await uow.tickets.get_ticket(
                ticket_id=ticket_id, ticket_model=ticket_model, user_id=user_id
            )

            return ticket

    @staticmethod
    async def get_tickets(
        uow: UnitOfWork,
        pagination: Optional[Params] = None,
        ticket_model: Optional[TicketModel] = None,
        user_id: Optional[int] = None,
    ):
        """Возвращает тикеты по переданным аргументам"""
        async with uow:
            offset = None
            limit = None
            if pagination:
                pagination_raw_params = pagination.to_raw_params()
                offset = pagination_raw_params.offset
                limit = pagination_raw_params.limit

            tickets = await uow.tickets.get_all_tickets(
                user_id=user_id, ticket_model=ticket_model, offset=offset, limit=limit
            )
            return tickets

    @staticmethod
    async def create_ticket_base(
        uow: UnitOfWork,
        ticket_type: TicketType,
        ticket_schema: TicketCreateSchema,
        object_class: TicketAvailableObjectClasses,
        object_id: int,
        user: User,
        images: Optional[List[UploadFile]] = None,
        images_urls: Optional[List[str]] = None,
    ):
        """
        Создаёт объект класса TicketBase
        :raises ValueError: If object_class is not an instance of TicketAvailableObjectClasses
        :raises NoResultFound: If object by id does not exist
        """
        async with uow:
            # Первым делом делаем проверку object_class и object_id - существует ли элемент

            if not isinstance(object_class, TicketAvailableObjectClasses):
                raise ValueError(
                    "object_class is not an instance of TicketAvailableObjectClasses"
                )
            object_class_inst = object_class.get_class()
            object_repo = await uow.get_repo_by_class(model_class=object_class_inst)
            await object_repo.get(
                obj_id=object_id
            )  # Если не найден - выкинет исключение NoResultFound
            # if not obj:
            #     raise ValueError("Object does not exist")

            # Поскольку у нас CreateSchema -некоторые данные придётся дополнить,
            # т.к. они либо достаются из query-параметров, либо из других мест... в целом, обычная процедура
            ticket_data = ticket_schema.model_dump()
            ticket_data["ticket_type"] = ticket_type.value
            ticket_data["user_id"] = user.id
            ticket_data["object_class"] = object_class.value
            ticket_data["object_id"] = object_id

            # Создание обращения
            ticket = await uow.tickets.create(ticket_data)

            # Обработка и загрузка изображений
            cloud_files: list[CloudFile] = (
                await CloudStorageService.upload_files_to_yandex_disk(
                    images=images, images_urls=images_urls
                )
            )

            # Создание объектов изображений в базе данных и их привязка к билету
            image_tickets: list[ImageTicket] = []
            for cloud_file in cloud_files:
                image_create = ImageTicketCreateSchema(
                    image_url=cloud_file.public_url,
                    public_key=cloud_file.public_key,
                    file_path=cloud_file.file_path,
                    blurhash=cloud_file.blurhash,
                    ticket_id=ticket.id,
                )
                # Чтобы не создавать одинаковые картинки - прикрепляем уже существующую.
                exist_image = await uow.images_ticket.filter(
                    image_url=image_create.image_url
                )
                if exist_image:
                    image_tickets.append(exist_image[0])
                else:
                    image_tickets.append(await uow.images_ticket.create(image_create))

            # Привязка изображений к билету
            ticket.images = image_tickets

            # ticket = await uow.tickets.create(obj_data=ticket_data)

            await uow.commit()
            return ticket

    @staticmethod
    async def approve_ticket_base(
        uow: UnitOfWork,
        moderator: Moderator,
        moderator_comment: str | None,
        ticket_id: int,
    ):
        """
        Подтверждает тикет

        :raises ValueError: Если тикет уже подтверждён
        """
        async with uow:
            # Получаем объект TicketBase в БД
            ticket: TicketBase = await uow.tickets.get(obj_id=ticket_id)

            if ticket.status == TicketStatus.APPROVED:
                raise ValueError("Уже подтверждено")

            ticket.status = TicketStatus.APPROVED

            # "Присоединяем" модератора к тикету.
            ticket.moderator_id = moderator.id
            # Добавляем комментарий от модератора, если есть
            ticket.moderator_comment = moderator_comment

            await uow.session.flush()
            await uow.session.refresh(ticket)
            await uow.commit()
            return ticket

    @staticmethod
    async def reject_ticket_base(
        uow: UnitOfWork,
        moderator: Moderator,
        moderator_comment: str | None,
        ticket_id: int,
    ):
        async with uow:
            # Получаем объект TicketBase в БД
            ticket: TicketBase = await uow.tickets.get(obj_id=ticket_id)

            if ticket.status != TicketStatus.PENDING:
                raise ValueError("Тикет не в статусе ожидания")

            ticket.status = TicketStatus.REJECTED

            # "Присоединяем" модератора к тикету.
            ticket.moderator_id = moderator.id
            # Добавляем комментарий от модератора, если есть
            ticket.moderator_comment = moderator_comment

            await uow.session.flush()
            await uow.session.refresh(ticket)
            await uow.commit()
            return ticket

    # endregion Ticket

    # region TicketArtwork

    @staticmethod
    async def create_ticket_artwork(
        uow: UnitOfWork,
        user: User,
        ticket_artwork_schema: TicketArtworkCreateSchema,
        images: Optional[List[UploadFile]] = None,
        images_urls: Optional[List[str]] = None,
        thumbnail_image_index: Optional[int] = None,
    ):
        async with uow:
            if not thumbnail_image_index:
                thumbnail_image_index = 0

            ticket_data: dict = ticket_artwork_schema.model_dump(mode="json")

            ticket_data["ticket_type"] = TicketType.CREATE
            ticket_data["user_id"] = user.id
            ticket_data["object_class"] = TicketAvailableObjectClasses.ARTWORK
            ticket_data["object_id"] = None

            # Создание тикета без информации об артворке и изображениях
            ticket: TicketArtwork = await uow.tickets_artwork.create(ticket_data)

            # Обработка и загрузка изображений
            cloud_files: list[CloudFile] = (
                await CloudStorageService.upload_files_to_yandex_disk(
                    images=images, images_urls=images_urls
                )
            )

            # Создание объектов изображений в базе данных и их привязка к билету
            image_tickets: list[ImageTicket] = []
            for cloud_file in cloud_files:
                image_create = ImageTicketCreateSchema(
                    image_url=cloud_file.public_url,
                    public_key=cloud_file.public_key,
                    file_path=cloud_file.file_path,
                    blurhash=cloud_file.blurhash,
                    ticket_id=ticket.id,
                )
                # Чтобы не создавать одинаковые картинки - прикрепляем уже существующую.
                exist_image = await uow.images_ticket.filter(
                    image_url=image_create.image_url
                )
                if exist_image:
                    image_tickets.append(exist_image[0])
                else:
                    image_tickets.append(await uow.images_ticket.create(image_create))

            # Привязка изображений к билету
            ticket.images = image_tickets

            # Добавление информации об артворке и изображениях к тикету
            if ticket_data.get("artwork_data").get("location"):
                if 0 <= thumbnail_image_index < len(cloud_files):
                    img = cloud_files[thumbnail_image_index]
                    ticket_data["artwork_data"]["location"][
                        "thumbnail_image"
                    ] = img.public_url

            # Обновление тикета с информацией об артворке и изображениях
            # ticket = await uow.tickets_artwork.edit(ticket.id, ticket_data)
            ticket.artwork_data = ticket_data["artwork_data"]

            await uow.commit()
            return ticket

    @staticmethod
    async def approve_ticket_artwork(
        uow: UnitOfWork,
        moderator: Moderator,
        moderator_comment: str | None,
        ticket_artwork_id: int,
    ):
        """
        Подтверждает тикет и создаёт объект на основе artwork_data

        :raises ValueError: Если тикет уже подтверждён
        """
        async with uow:
            # Получаем объект TicketArtwork в БД
            ticket_artwork: TicketArtwork = await uow.tickets_artwork.get(
                obj_id=ticket_artwork_id
            )

            if ticket_artwork.status == TicketStatus.APPROVED:
                raise ValueError("Уже подтверждено")

            # "Присоединяем" модератора к тикету.
            ticket_artwork.moderator_id = moderator.id
            # ticket_artwork.moderator = moderator

            # Валидируем данные и получаем из ticket_artwork.artwork_data -> ArtworkCreateSchema
            ticket_artwork_data: dict = (
                ticket_artwork.artwork_data
            )  # Тут, по факту, ArtworkCreateSchema
            ticket_artwork_schema: ArtworkCreateSchema = ArtworkCreateSchema(
                **ticket_artwork_data
            )

            # artwork_dict = ticket_artwork_data.model_dump(exclude={"location", "images"})
            # ticket_artwork_data.pop("location", None)
            # ticket_artwork_data.pop("images", None)

            # Для удобства. Всё равно переделывать.

            # Исключаю объект локации, т.к. его нужно создать отдельно и присвоить artwork'у

            artwork_dict = ticket_artwork_schema.model_dump(
                exclude={"location"}, mode="json"
            )

            artwork_dict["added_by_user_id"] = ticket_artwork.user_id

            artwork_dict["artist"] = []
            if ticket_artwork_schema.artist:
                for artist_id in ticket_artwork_schema.artist:
                    try:
                        artist = await ArtistsService.get_artist_by_id(
                            uow=uow, artist_id=artist_id
                        )
                        artwork_dict["artist"].append(artist)
                    except ObjectNotFoundException:
                        continue

            artwork_dict["festival_id"] = (
                ticket_artwork_schema.festival_id
                if ticket_artwork_schema.festival_id
                else None
            )

            # region Создание Арт-объекта из подготовленного словаря
            artwork = await uow.artworks.create(artwork_dict)

            # if artwork.artist_id:
            #     artwork.artist = await uow.artist.get(artwork.artist_id)
            # else:
            #     artwork.artist = None

            images_artwork_list: list[ImageArtwork] = list()
            for image in ticket_artwork.images:
                # image = await uow.images.filter(image_url=image.get("image_url"))
                # image = image[0]
                image_artwork_schema = ImageArtworkCreateSchema(
                    artwork_id=artwork.id,
                    image_url=image.image_url,
                    public_key=image.public_key,
                    blurhash=image.blurhash,
                    file_path=image.file_path,
                )

                image_artwork: ImageArtwork = await uow.images_artwork.create(
                    image_artwork_schema
                )
                images_artwork_list.append(image_artwork)

            artwork.images = images_artwork_list

            if ticket_artwork_schema.location is not None:
                thumbnail_image_id = None
                thumbnail_image_url: str = ticket_artwork_data.get("location").get(
                    "thumbnail_image"
                )  # url
                if thumbnail_image_url:
                    exist_image = await uow.images_artwork.filter(
                        image_url=thumbnail_image_url
                    )
                    if exist_image:
                        thumbnail_image_id = exist_image[0].id

                artwork_location_schema = ArtworkLocationTicketCreateSchema(
                    artwork_id=artwork.id,
                    latitude=ticket_artwork_schema.location.latitude,
                    longitude=ticket_artwork_schema.location.longitude,
                    address=ticket_artwork_schema.location.address,
                    thumbnail_image_id=thumbnail_image_id,
                )

                # Создаём объект ArtworkLocation и присваиваем его id к Artwork
                artwork_location: ArtworkLocation = await uow.artwork_locations.create(
                    artwork_location_schema
                )

                artwork.location_id = artwork_location.id

            # Добавляем artwork.id к TicketArtwork
            ticket_artwork.object_id = artwork.id
            # Изменяем статус заявки
            ticket_artwork.status = TicketStatus.APPROVED
            # Добавляем сообщение от модератора, если есть
            ticket_artwork.moderator_comment = moderator_comment
            # endregion
            await uow.session.flush()
            await uow.session.refresh(artwork)
            await uow.session.refresh(ticket_artwork)
            await uow.commit()
            return ticket_artwork

    @staticmethod
    async def reject_ticket_artwork(
        uow: UnitOfWork,
        moderator: Moderator,
        moderator_comment: str | None,
        ticket_artwork_id: int,
    ):
        async with uow:
            # Получаем объект TicketArtwork в БД
            ticket_artwork: TicketArtwork = await uow.tickets_artwork.get(
                obj_id=ticket_artwork_id
            )

            if ticket_artwork.status != TicketStatus.PENDING:
                raise ValueError("Тикет не в статусе ожидания")

            ticket_artwork.status = TicketStatus.REJECTED

            # "Присоединяем" модератора к тикету.
            ticket_artwork.moderator_id = moderator.id
            # Добавляем комментарий от модератора, если есть
            ticket_artwork.moderator_comment = moderator_comment

            await uow.session.flush()
            await uow.session.refresh(ticket_artwork)
            await uow.commit()
            return ticket_artwork

    # endregion TicketArtwork

    @staticmethod
    async def delete_all_tickets(uow: UnitOfWork):
        async with uow:
            await uow.tickets.delete_all()

    @staticmethod
    async def get_all_tickets(
        uow: UnitOfWork,
        ticket_model: Optional[TicketModel] = None,
    ):
        async with uow:
            if ticket_model:
                tickets = await uow.tickets.get_all_tickets_by_ticket_model(
                    ticket_model=ticket_model
                )
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
            #         ticket_model=ticket_model
            #     )
            # else:
            #     tickets = await uow.tickets.get_all()

            return await uow.tickets.count()
