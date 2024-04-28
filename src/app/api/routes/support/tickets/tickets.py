from enum import Enum
from typing import Optional, Annotated, List

from fastapi import APIRouter, HTTPException, status, Depends, Body, UploadFile, File
from sqlalchemy.exc import NoResultFound

from app.api.routes.common import (
    generate_detail,
    ErrorCode,
    generate_response,
    ErrorModel,
)
from app.api.utils import is_image
from app.api.utils.libs.fastapi_filter import FilterDepends
from app.api.utils.libs.fastapi_filter.contrib.sqlalchemy import Filter
from app.api.utils.paginator import MyParams
from app.modules import User, Moderator
from app.modules.tickets.schemas.ticket_artwork import (
    ArtworkTicketCreateSchema,
    ArtworkTicketReadSchema,
    ArtworkTicketUpdateSchema,
)
from app.modules.tickets.schemas.ticket_base import TicketReadSchema, TicketCreateSchema
from app.modules.tickets.utils.classes import (
    TicketModel,
    TicketRegistry,
)
from app.modules.tickets.utils.types import (
    TicketReadSchemaType,
    TicketCreateSchemaType,
)
from app.modules.users.fastapi_users_config import current_user
from app.services.artworks import ArtworksService
from app.services.tickets import TicketsService
from app.utils.dependencies import UOWDep, get_current_moderator

router = APIRouter()


@router.get(
    "/my",
    response_model=list[TicketReadSchemaType],
    description="ДЛЯ ПОЛЬЗОВАТЕЛЕЙ! Выводит список тикетов авторизованного пользователя.",
)
# @cache(expire=15)
async def show_tickets(
        uow: UOWDep,
        user: User = Depends(current_user),
        ticket_model: TicketModel = None,
        pagination: MyParams = Depends(),
):
    tickets = await TicketsService().get_tickets(uow=uow, pagination=pagination, ticket_model=ticket_model,
                                                 user_id=user.id)
    return tickets


@router.get(
    "/{ticket_id}",
    response_model=TicketReadSchemaType,
    description="""Выводит тикет. `Вероятно, выбор ticket_model можно вырезать? Он так и так, если не передать, 
    выведет тикет, просто с ticket_model - конкретный тип ожидает` 
    **Кстати, можно немного по другому реализовать фильтрацию тикетов по пользователю... и не знаю стоит ли оно того. 
    Короче, сейчас, даже если такой тикет есть в базе, но к нему обращается не его создатель, то будет 404 - не найдено,
    мол такого объекта вообще не существует. С одной стороны - ок. Но с другой.. 
    Наверное лучше через 403 Forbidden, типо "Нет доступа".**
    
    
    Если роль пользователя:
    - user, artist - ответ будет приходить только на тикеты, созданные этим пользователем. 
    - modeartor - может получить тикет по любому ticket_id
    """,
)
# @cache(expire=15)
async def show_ticket(
        uow: UOWDep,
        ticket_id: int,
        ticket_model: TicketModel = None,
        user: User = Depends(current_user)):
    try:
        if user.is_moderator:
            ticket = await TicketsService().get_ticket(
                uow=uow, ticket_id=ticket_id, ticket_model=ticket_model
            )
        else:
            ticket = await TicketsService().get_ticket(
                uow=uow, ticket_id=ticket_id, ticket_model=ticket_model, user_id=user.id
            )

        return ticket
    except NoResultFound:
        # Обработка случая, когда запись не найдена
        # Вернуть 404 ошибку или пустой объект
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=generate_detail(
                error_code=ErrorCode.OBJECT_NOT_FOUND, message="Ticket not found"
            ),
        )


@router.get(
    "/user/{user_id}",
    response_model=list[TicketReadSchemaType],
    description="ДЛЯ МОДЕРАТОРОВ! Выводит список тикетов конкретного пользователя."
)
# @cache(expire=15)
async def show_tickets(
        uow: UOWDep,
        user_id: int,
        moderator: Moderator = Depends(get_current_moderator),
        ticket_model: TicketModel = None,
        pagination: MyParams = Depends(),
):
    tickets = await TicketsService().get_tickets(uow=uow, ticket_model=ticket_model,
                                                 pagination=pagination, user_id=user_id)
    return tickets


@router.get(
    "/",
    response_model=list[TicketReadSchemaType],
    description="ДЛЯ МОДЕРАТОРОВ! Выводит список всех тикетов.",
)
# @cache(expire=15)
async def show_tickets(
        uow: UOWDep,
        moderator: Moderator = Depends(get_current_moderator),
        ticket_model: TicketModel = None,
        pagination: MyParams = Depends(),
):
    tickets = await TicketsService().get_tickets(
        uow=uow, pagination=pagination, ticket_model=ticket_model
    )
    return tickets


@router.post(
    "/",
    response_model=TicketReadSchemaType,
    description="Создаёт обычный текстовый тикет.",
)
async def create_ticket(
        uow: UOWDep,
        user: User = Depends(current_user),
        ticket_schema: TicketCreateSchema = Body(...),
):
    ticket = await TicketsService.create_ticket(
        uow=uow, user=user, ticket_schema=ticket_schema
    )

    return ticket


@router.post(
    "/artwork/",
    response_model=TicketReadSchemaType,
    description="Создаёт тикет.",
    responses={
        status.HTTP_400_BAD_REQUEST: generate_response(
            error_model=ErrorModel,
            error_code=ErrorCode.INVALID_IMAGE_FILE_EXTENSION,
            summary="Images validation failed",
            message="Invalid image file extension",
            data={"filename": "filename.ext"},
        ),
    },
)
async def create_artwork_ticket(
        uow: UOWDep,
        user: User = Depends(current_user),
        artwork_ticket_schema: ArtworkTicketCreateSchema = Body(...),
        thumbnail_image_index: Annotated[int, Body()] = None,
        images: Annotated[
            List[UploadFile],
            File(..., description="Разрешены '.webp', '.jpg', '.jpeg', '.png', '.heic'"),
        ] = None,
):
    if images:
        for image in images:
            if not is_image(image):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=generate_detail(
                        error_code=ErrorCode.INVALID_IMAGE_FILE_EXTENSION,
                        message="Invalid image file extension",
                        data={"filename": image.filename},
                    ),
                )

    artwork_ticket = await TicketsService.create_artwork_ticket(
        uow=uow,
        user=user,
        artwork_ticket_schema=artwork_ticket_schema,
        thumbnail_image_index=thumbnail_image_index,
        images=images,
    )

    return artwork_ticket


# @router.patch(
#     "/{artwork_ticket_id}",
#     response_model=ArtworkTicketReadSchema,
#     description="ДЛЯ ПОЛЬЗОВАТЕЛЯ!!! Даёт возможность изменить поля",
# )
# async def update_artwork_ticket(
#     uow: UOWDep,
#     artwork_ticket_id: int,
#     user: User = Depends(current_user),
#     artwork_ticket_schema: ArtworkTicketUpdateSchema = Body(None),
#     thumbnail_image_index: Annotated[int, Body()] = None,
#     images: Annotated[
#         List[UploadFile],
#         File(..., description="Разрешены '.webp', '.jpg', '.jpeg', '.png', '.heic'"),
#     ] = None,
# ):
#     if images:
#         for image in images:
#             if not is_image(image):
#                 raise HTTPException(
#                     status_code=status.HTTP_400_BAD_REQUEST,
#                     detail=generate_detail(
#                         error_code=ErrorCode.INVALID_IMAGE_FILE_EXTENSION,
#                         message="Invalid image file extension",
#                         data={"filename": image.filename},
#                     ),
#                 )
#
#     artwork_ticket = await TicketsService.update_artwork_ticket(
#         uow=uow,
#         artwork_ticket_id=artwork_ticket_id,
#         user=user,
#         artwork_ticket_schema=artwork_ticket_schema,
#         thumbnail_image_index=thumbnail_image_index,
#         images=images,
#     )
#
#     return artwork_ticket


@router.patch(
    "/artwork/approve/{artwork_ticket_id}",
    response_model=ArtworkTicketReadSchema,
    description="ДЛЯ МОДЕРАТОРА!!! Подтвердить тикет связанный с арт-объектом.",
)
async def approve_artwork_ticket(
        uow: UOWDep,
        artwork_ticket_id: int,
        moderator: Moderator = Depends(get_current_moderator),
):
    artwork_ticket = await TicketsService.approve_artwork_ticket(
        uow=uow, moderator=moderator, artwork_ticket_id=artwork_ticket_id
    )

    return artwork_ticket


@router.patch(
    "/artwork/reject/{artwork_ticket_id}",
    response_model=ArtworkTicketReadSchema,
    description="ДЛЯ МОДЕРАТОРА!!! Отклонить тикет связанный с арт-объектом.",
)
async def approve_artwork_ticket(
        uow: UOWDep,
        artwork_ticket_id: int,
        moderator: Moderator = Depends(get_current_moderator),
):
    artwork_ticket = await TicketsService.reject_artwork_ticket(
        uow=uow, moderator=moderator, artwork_ticket_id=artwork_ticket_id
    )

    return artwork_ticket

# @router.post(
#     "/",
#     response_model=TicketReadSchemaType,
#     description="Создаёт обычный текстовый тикет."
# )
# async def create_ticket(
#         uow: UOWDep,
#         ticket_model: TicketModel = None,
#         user: User = Depends(current_user),
#         ticket_data: TicketCreateSchemaType = Body(...),
#         thumbnail_image_index: Annotated[int, Body()] = None,
#         images: Annotated[
#             List[UploadFile],
#             File(..., description="Разрешены '.webp', '.jpg', '.jpeg', '.png', '.heic'"),
#         ] = None,
# ):
#
# @router_artworks.post(
#     path="/",
#     response_model=ArtworkReadSchema,
#     status_code=status.HTTP_201_CREATED,
#     description="После создания арт-объекта, его статус модерации будет 'Ожидает проверки'.",
#     responses={
#         status.HTTP_400_BAD_REQUEST: generate_response(
#             error_model=ErrorModel,
#             error_code=ErrorCode.INVALID_IMAGE_FILE_EXTENSION,
#             summary="Images validation failed",
#             message="Invalid image file extension",
#             data={"filename": "filename.ext"},
#         ),
#     },
# )
# async def create_artwork(
#     uow: UOWDep,
#     user: User = Depends(current_user),
#     artwork_data: ArtworkCreateSchema = Body(...),
#     thumbnail_image_index: Annotated[int, Body()] = None,
#     images: Annotated[
#         List[UploadFile],
#         File(..., description="Разрешены '.webp', '.jpg', '.jpeg', '.png', '.heic'"),
#     ] = None,
# ):
#     if images:
#         for image in images:
#             if not is_image(image):
#                 raise HTTPException(
#                     status_code=status.HTTP_400_BAD_REQUEST,
#                     detail=generate_detail(
#                         error_code=ErrorCode.INVALID_IMAGE_FILE_EXTENSION,
#                         message="Invalid image file extension",
#                         data={"filename": image.filename},
#                     ),
#                 )
#
#     artwork = await ArtworksService().create_artwork(
#         uow=uow,
#         user=user,
#         artwork_schema=artwork_data,
#         images=images,
#         thumbnail_image_index=thumbnail_image_index,
#     )
#
#     # artwork_images = await ArtworksService().
#
#     return artwork
#
#
# # @cache(expire=60, namespace="show_artworks")
# # await FastAPICache.clear(namespace="show_artworks")
# @router_artworks.get(
#     "/",
#     response_model=Page[ArtworkReadSchema],
#     description=f"""Выводит список подтверждённых арт-объектов, используя пагинацию. Лимит: 50 объектов.\n
#     Поля для сортировки: {", ".join(ArtworkFilter.Constants.ordering_model_fields)}\n
#     Поля используемые в поиске: {", ".join(ArtworkFilter.Constants.search_model_fields)}""",
# )
# async def show_artworks(
#     uow: UOWDep,
#     pagination: MyParams = Depends(),
#     filters: Filter = FilterDepends(ArtworkFilter),
# ):
#     artworks = await ArtworksService().get_approved_artworks(uow, pagination, filters)
#     return paginate(artworks, pagination)
#
#
# @router_artworks.get(
#     "/{artwork_id}",
#     response_model=ArtworkReadSchema,
#     description="Выводит арт-объект по его ID.",
#     responses={
#         status.HTTP_404_NOT_FOUND: generate_response(
#             error_model=ErrorModel,
#             error_code=ErrorCode.OBJECT_NOT_FOUND,
#             summary="Object not found",
#             message="Artwork not found",
#         )
#     },
# )
# async def show_artwork(artwork_id: int, uow: UOWDep):
#     try:
#         artwork = await ArtworksService().get_artwork(uow, artwork_id)
#         return artwork
#     except NoResultFound:
#         # Обработка случая, когда запись не найдена
#         # Вернуть 404 ошибку или пустой объект
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=generate_detail(
#                 error_code=ErrorCode.OBJECT_NOT_FOUND, message="Artwork not found"
#             ),
#         )
#
#
# @router_artworks.patch(
#     "/{artwork_id}",
#     response_model=ArtworkForModeratorReadSchema,
#     description="Метод для редактирования отдельных полей арт-объекта.",
#     responses={
#         status.HTTP_404_NOT_FOUND: generate_response(
#             error_model=ErrorModel,
#             error_code=ErrorCode.OBJECT_NOT_FOUND,
#             summary="Object not found",
#             message="Artwork not found",
#         )
#     },
# )
# async def update_artwork(
#     artwork_id: int, artwork_data: ArtworkUpdateSchema, uow: UOWDep
# ):
#     try:
#         artwork = await ArtworksService().update_artwork(uow, artwork_id, artwork_data)
#         return artwork
#     except NoResultFound:
#         # Обработка случая, когда запись не найдена
#         # Вернуть 404 ошибку или пустой объект
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=generate_detail(
#                 error_code=ErrorCode.OBJECT_NOT_FOUND, message="Artwork not found"
#             ),
#         )
#
#
# # ToDO: доработать метод удаления. Возвращает мало информации + нет response_model.
# @router_artworks.delete(
#     "/{artwork_id}",
#     description="Удаляет арт-объект и его связные сущности, включая изображения.",
#     status_code=status.HTTP_200_OK,
#     responses={
#         status.HTTP_404_NOT_FOUND: generate_response(
#             error_model=ErrorModel,
#             error_code=ErrorCode.OBJECT_NOT_FOUND,
#             summary="Object not found",
#             message="Artwork not found",
#         )
#     },
# )
# async def delete_artwork(artwork_id: int, uow: UOWDep):
#     try:
#         await ArtworksService().delete_artwork(uow, artwork_id)
#         return JSONResponse(
#             content={"message": "Object deleted successfully"},
#             status_code=status.HTTP_200_OK,
#         )
#     except NoResultFound:
#         # Обработка случая, когда запись не найдена
#         # Вернуть 404 ошибку или пустой объект
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=generate_detail(
#                 error_code=ErrorCode.OBJECT_NOT_FOUND, message="Artwork not found"
#             ),
#         )
#     # except ObjectNotFound as exc:
#     #     raise exc
