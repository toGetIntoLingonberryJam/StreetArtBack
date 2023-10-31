from app.modules.artworks.schemas.artwork import ArtworkCreate, ArtworkEdit
from app.utils.service import BaseService
from app.utils.unit_of_work import UnitOfWork


class ArtworksService:
    async def create_artwork(self, uow: UnitOfWork, artwork_schem: ArtworkCreate):
        artwork_dict = artwork_schem.model_dump()
        async with uow:
            artwork = await uow.artworks.create(artwork_dict)
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
