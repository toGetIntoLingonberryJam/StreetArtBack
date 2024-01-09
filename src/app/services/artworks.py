from typing import Optional, List

from fastapi import UploadFile
from fastapi_filter.contrib.sqlalchemy import Filter
from fastapi_pagination import Params

from app.modules.artworks.models.artwork import Artwork
from app.modules.artworks.models.artwork_moderation import ArtworkModerationStatus
from app.modules.artworks.schemas.artwork import ArtworkCreate, ArtworkEdit
from app.modules.artworks.schemas.artwork_image import ArtworkImageCreate
from app.modules.artworks.schemas.artwork_moderation import ArtworkModerationCreate
from app.modules.users.models import User
from app.utils.cloud_storage_config import upload_to_yandex_disk
from app.utils.unit_of_work import UnitOfWork


class ArtworksService:
    async def create_artwork(
        self,
        uow: UnitOfWork,
        user: User,
        artwork_schem: ArtworkCreate,
        images: Optional[List[UploadFile]] = None,
        thumbnail_image_index: Optional[int] = None,
    ):
        location_data = artwork_schem.location

        artwork_dict = artwork_schem.model_dump(exclude={"location"})

        artwork_dict["added_by_user_id"] = user.id
        artwork_dict["artist_id"] = (
            artwork_schem.artist_id if artwork_schem.artist_id else None
        )
        artwork_dict["festival_id"] = (
            artwork_schem.festival_id if artwork_schem.festival_id else None
        )

        async with uow:
            artwork = await uow.artworks.create(artwork_dict)

            # Добавление связи ArtworkModeration
            artwork.moderation = await uow.artwork_moderation.create(
                ArtworkModerationCreate(artwork_id=artwork.id)
            )

            # Добавление связи ArtworkLocation
            artwork.location = await uow.artwork_locations.create(location_data)

            if images:
                images_data_list = list()
                artwork_images = list()
                unique_image_urls = set()

                for image in images:
                    public_image_url = await upload_to_yandex_disk(image)

                    image_data = {
                        "image_url": public_image_url,
                        "artwork_id": artwork.id,
                    }

                    # ToDo: Добавлять созданную схему во все схемы, для дальнейшего создания объектов одним запросом к
                    #  БД. создать create_many
                    # Создание объекта Pydantic
                    image_create = ArtworkImageCreate(**image_data)

                    # Проверка отсутствия image_url в уникальных
                    if image_create.image_url not in unique_image_urls:
                        unique_image_urls.add(image_create.image_url)
                        images_data_list.append(image_create)

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

    async def get_artworks_by_moderation_status(
        self,
        uow: UnitOfWork,
        moderation_status: ArtworkModerationStatus,
        pagination: Params | None = None,
        filters: Filter | None = None,
        **filter_by
    ) -> list[Artwork]:
        async with uow:
            offset: int = 0
            limit: int | None = None

            if pagination:
                pagination_raw_params = pagination.to_raw_params()
                offset = pagination_raw_params.offset
                limit = pagination_raw_params.limit

            artworks = await uow.artworks.get_all(
                offset=offset,
                limit=limit,
                # pagination=pagination,
                filters=filters,
                moderation={
                    uow.artwork_moderation.model.status: moderation_status  # Можно string
                },
                filter_by=filter_by,
            )
            return artworks

    async def get_pending_artworks(
        self,
        uow: UnitOfWork,
        pagination: Params | None = None,
        filters: Filter | None = None,
        **filter_by
    ) -> list[Artwork]:
        return await self.get_artworks_by_moderation_status(
            uow=uow,
            moderation_status=ArtworkModerationStatus.PENDING,
            pagination=pagination,
            filters=filters,
            filter_by=filter_by,
        )

    async def get_approved_artworks(
        self,
        uow: UnitOfWork,
        pagination: Params | None = None,
        filters: Filter | None = None,
        **filter_by
    ) -> list[Artwork]:
        return await self.get_artworks_by_moderation_status(
            uow=uow,
            moderation_status=ArtworkModerationStatus.APPROVED,
            pagination=pagination,
            filters=filters,
            filter_by=filter_by,
        )

    async def get_rejected_artworks(
        self,
        uow: UnitOfWork,
        pagination: Params | None = None,
        filters: Filter | None = None,
        **filter_by
    ) -> list[Artwork]:
        return await self.get_artworks_by_moderation_status(
            uow=uow,
            moderation_status=ArtworkModerationStatus.REJECTED,
            pagination=pagination,
            filters=filters,
            filter_by=filter_by,
        )

    async def get_artwork(self, uow: UnitOfWork, artwork_id: int):
        async with uow:
            artwork = await uow.artworks.get(artwork_id)
            return artwork

    async def get_all_artworks(self, uow: UnitOfWork):
        async with uow:
            artworks = await uow.artworks.get_all()
            return artworks

    async def get_artworks_locations(self, uow: UnitOfWork):
        async with uow:
            # artworks = await uow.artworks.get_all()
            artworks = await self.get_approved_artworks(uow=uow)

            locations = [
                artwork.location for artwork in artworks if artwork.location is not None
            ]

            return locations

    async def edit_artwork(
        self, uow: UnitOfWork, artwork_id: int, artwork_schem: ArtworkEdit
    ):
        location_dict = (
            artwork_schem.location.model_dump(exclude_unset=True)
            if artwork_schem.location
            else None
        )
        moderation_dict = (
            artwork_schem.moderation.model_dump(exclude_unset=True)
            if artwork_schem.moderation
            else None
        )
        # location_dict = artwork_schem.location.model_dump(exclude_unset=True)
        # moderation_dict = artwork_schem.moderation.model_dump(exclude_unset=True)

        artwork_dict = artwork_schem.model_dump(
            exclude_unset=True, exclude={"location", "moderation"}
        )

        async with uow:
            # Редактирование арт-объекта
            artwork = await uow.artworks.edit(artwork_id, artwork_dict)

            if location_dict:
                # Редактирование локации арт-объекта
                # location_id = artwork.location.id
                await uow.artwork_locations.edit(artwork.location.id, location_dict)

            if moderation_dict:
                # Редактирование модерации арт-объекта
                await uow.artwork_moderation.edit(
                    artwork.moderation.id, moderation_dict
                )

            await uow.commit()

            return artwork

        #
        #
        #     # artwork = await uow.artworks.create(artwork_dict)
        #     #
        #     # artwork_moderation = await uow.artwork_moderation.create(
        #     #     ArtworkModerationCreate(artwork_id=artwork.id)
        #     # )
        #     # artwork.moderation = artwork_moderation
        #     #
        #     # if location_data:
        #     #     artwork_location = await uow.artwork_locations.create(location_data)
        #     #     # Привязка Artwork к ArtworkLocation
        #     #     artwork.location = artwork_location
        #     #
        #     # if images:
        #     #     images_data_list = list()
        #
        #
        #
        # artwork_dict = artwork_schem.model_dump()
        # async with uow:
        #     await uow.artworks.edit(artwork_id, artwork_dict)

    async def delete_artwork(self, uow: UnitOfWork, artwork_id: int):
        async with uow:
            artwork = await self.get_artwork(uow=uow, artwork_id=artwork_id)
            artwork_images = artwork.images
            for img in artwork_images:
                print(img.image_url)  # ToDo: Оформить удалялку с хранилища для картинок

            await uow.artworks.delete(artwork_id)
            await uow.commit()

        # artwork_dict = artwork_schem.model_dump()
        # async with uow:
        #     artwork = await uow.artworks.create(artwork_dict)
        #     await uow.commit()
        #     return artwork


# class TasksService:
#     async def add_task(self, uow: IUnitOfWork, task: TaskSchemaAdd):
#         tasks_dict = task.model_dump()
#         async with uow:
#             task_id = await uow.tasks.add_one(tasks_dict)
#             await uow.commit()
#             return task_id
#
#     async def get_tasks(self, uow: IUnitOfWork):
#         async with uow:
#             tasks = await uow.tasks.find_all()
#             return tasks
#
#     async def edit_task(self, uow: IUnitOfWork, task_id: int, task: TaskSchemaEdit):
#         tasks_dict = task.model_dump()
#         async with uow:
#             await uow.tasks.edit_one(task_id, tasks_dict)
#
#             curr_task = await uow.tasks.find_one(id=task_id)
#             task_history_log = TaskHistorySchemaAdd(
#                 task_id=task_id,
#                 previous_assignee_id=curr_task.assignee_id,
#                 new_assignee_id=task.assignee_id
#             )
#             task_history_log = task_history_log.model_dump()
#             await uow.task_history.add_one(task_history_log)
#             await uow.commit()
#
#     async def get_task_history(self, uow: IUnitOfWork):
#         async with uow:
#             history = await uow.task_history.find_all()
#             return history
