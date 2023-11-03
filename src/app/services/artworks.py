import shutil
from typing import Optional, List

import aiofiles
from fastapi import UploadFile

from app.modules.artworks.schemas.artwork import ArtworkCreate, ArtworkEdit
from app.modules.artworks.schemas.artwork_image import ArtworkImageCreate
from app.utils.service import BaseService
from app.utils.unit_of_work import UnitOfWork


class ArtworksService:
    async def create_artwork(self, uow: UnitOfWork, artwork_schem: ArtworkCreate,
                             images: Optional[List[UploadFile]] = None,
                             thumbnail_image_index: Optional[int] = None):
        location_data = artwork_schem.location

        artwork_dict = artwork_schem.model_dump(exclude={"location"})

        # artwork_location_dict = artwork_dict.pop('location')
        # artwork_images_dict = artwork_dict.pop('images')

        async with uow:
            artwork = await uow.artworks.create(artwork_dict)

            if location_data:
                artwork_location = await uow.artwork_locations.create(location_data)
                # Привязка Artwork к ArtworkLocation
                artwork.location = artwork_location

            if images:
                images_data_list = list()

                for image in images:
                    # Путь к папке, в которую нужно сохранить файл
                    save_path = f"static/{image.filename}"

                    # Открываем файл для записи в бинарном режиме и записываем в него данные из загруженного файла
                    # with open(save_path, "wb") as image_file:
                    #     shutil.copyfileobj(image.file, image_file)

                    async with aiofiles.open(save_path, 'wb') as image_file:
                        while content := await image.read(1024):  # async read chunk
                            await image_file.write(content)  # async write chunk

                    image_data = {'image_url': "http://localhost:8000/"+save_path, 'artwork_id': artwork.id}

                    # Добавляю созданную схему во все схемы, для дальнейшего создания объектов одним запросом к БД
                    images_data_list.append(ArtworkImageCreate(**image_data))

                artwork_images = [await uow.artwork_images.create(image_data) for image_data in images_data_list]

                # Привязка Artwork к ArtworkImage
                artwork.images = artwork_images

                if location_data:
                    if 0 <= thumbnail_image_index < len(artwork_images):
                        img = artwork_images[thumbnail_image_index]
                        img.generate_thumbnail_url()
                        artwork.location.thumbnail_image = img


            await uow.commit()
            return artwork

    async def get_artwork(self, uow: UnitOfWork, artwork_id: int):
        async with uow:
            artwork = await uow.artworks.get(artwork_id)
            return artwork

    async def get_artworks(self, uow: UnitOfWork):
        async with uow:
            artworks = await uow.artworks.get_all()
            return artworks

    async def get_artworks_locations(self, uow: UnitOfWork):
        async with uow:
            artworks = await uow.artworks.get_all()

            locations = [artwork.location for artwork in artworks if artwork.location is not None]

            return locations

    async def edit_artwork(self, uow: UnitOfWork, artwork_id: int, artwork_schem: ArtworkEdit):
        artwork_dict = artwork_schem.model_dump()
        async with uow:
            await uow.artworks.edit(artwork_id, artwork_dict)

    @staticmethod
    async def delete_artwork(uow: UnitOfWork, artwork_id: int):
        async with uow:
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
