from enum import Enum
from typing import Annotated, List, Optional, Union

from fastapi import (
    APIRouter,
    Body,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from sqlalchemy.exc import NoResultFound

from app.api.routes.common import (
    ErrorCode,
    ErrorModel,
    generate_detail,
    generate_response,
)
from app.api.utils.libs.fastapi_filter import FilterDepends
from app.api.utils.libs.fastapi_filter.contrib.sqlalchemy import Filter
from app.api.utils.paginator import MyParams
from app.api.utils.utils import raise_if_not_image
from app.modules.models import Moderator, User
from app.modules.tickets.schemas.ticket_artwork import (
    TicketArtworkCreateSchema,
    TicketArtworkReadSchema,
    TicketArtworkUpdateSchema,
)
from app.modules.tickets.schemas.ticket_base import TicketCreateSchema, TicketReadSchema
from app.modules.tickets.utils.classes import (
    TicketAvailableObjectClasses,
    TicketModel,
    TicketRegistry,
    TicketType,
)
from app.modules.tickets.utils.types import TicketCreateSchemaType, TicketReadSchemaType
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
    tickets = await TicketsService().get_tickets(
        uow=uow, pagination=pagination, ticket_model=ticket_model, user_id=user.id
    )
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
    user: User = Depends(current_user),
):
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
    description="ДЛЯ МОДЕРАТОРОВ! Выводит список тикетов конкретного пользователя.",
)
# @cache(expire=15)
async def show_tickets(
    uow: UOWDep,
    user_id: int,
    moderator: Moderator = Depends(get_current_moderator),
    ticket_model: TicketModel = None,
    pagination: MyParams = Depends(),
):
    tickets = await TicketsService().get_tickets(
        uow=uow, ticket_model=ticket_model, pagination=pagination, user_id=user_id
    )
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


# @router.post("/test-create/", response_model=TicketReadSchemaType)
# async def test_create_ticket(
#     uow: UOWDep,
#     ticket_model: TicketModel,
#     ticket_type: TicketType,
#     ticket_data: TicketCreateSchema | TicketArtworkCreateSchema = Body(
#         ...
#     ),  # ToDo: Придумать как отобразить в SwaggerUI. В текущий момент нет поддержки TypeVar.
#     #   TicketCreateSchemaType - "простаивает"
#     images: Annotated[
#         List[UploadFile],
#         File(..., description="Разрешены '.webp', '.jpg', '.jpeg', '.png', '.heic'"),
#     ] = None,
#     images_urls: Annotated[list[str], Body()] = None,
#     user: User = Depends(current_user),
# ):
#     pass


@router.post(
    "/",
    response_model=TicketReadSchemaType,
    description="Создаёт тикет 'есть неточности' на редактирование объекта (работы/автора/фестиваля). "
    "Текстовое поле + фото.",
)
async def create_edit_ticket(
    uow: UOWDep,
    ticket_schema: TicketCreateSchema = Body(...),
    object_class: TicketAvailableObjectClasses = Query(...),
    object_id: int = Query(...),
    images: Annotated[
        List[UploadFile],
        File(..., description="Разрешены '.webp', '.jpg', '.jpeg', '.png', '.heic'"),
    ] = None,
    # images_urls: Annotated[list[str], Body()] = None,
    user: User = Depends(current_user),
):
    raise_if_not_image(images)

    # ToDo: Обсудить возможность выбора типа тикета
    #   На данный момент - принудительно ставится EDIT.
    ticket_type: TicketType = TicketType.EDIT
    try:
        ticket = await TicketsService.create_ticket_base(
            uow=uow,
            user=user,
            ticket_type=ticket_type,
            ticket_schema=ticket_schema,
            object_class=object_class,
            object_id=object_id,
            images=images,
        )
    except ValueError:
        # Обработка случая, когда не получилось найти экземпляр класса по object_class
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=generate_detail(
                error_code=ErrorCode.OBJECT_NOT_FOUND,
                message="The Object class not found",
            ),
        )
    except NoResultFound:
        # Обработка случая, когда объект по классу и id не найден
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=generate_detail(
                error_code=ErrorCode.OBJECT_NOT_FOUND, message="The Object not found"
            ),
        )

    return ticket


@router.patch(
    "/approve/{ticket_id}",
    response_model=TicketReadSchema,
    description="Подтвердить тикет.",
)
async def approve_edit_ticket(
    uow: UOWDep,
    ticket_id: int,
    moderator_comment: str = Body(None),
    moderator: Moderator = Depends(get_current_moderator),
):
    ticket = await TicketsService.approve_ticket_base(
        uow=uow,
        moderator=moderator,
        moderator_comment=moderator_comment,
        ticket_id=ticket_id,
    )

    return ticket


@router.patch(
    "/reject/{ticket_id}",
    response_model=TicketReadSchema,
    description="Отклонить тикет.",
)
async def reject_edit_ticket(
    uow: UOWDep,
    ticket_id: int,
    moderator_comment: str = Body(None),
    moderator: Moderator = Depends(get_current_moderator),
):
    ticket = await TicketsService.reject_ticket_base(
        uow=uow,
        moderator=moderator,
        moderator_comment=moderator_comment,
        ticket_id=ticket_id,
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
async def create_ticket_artwork(
    uow: UOWDep,
    user: User = Depends(current_user),
    ticket_artwork_schema: TicketArtworkCreateSchema = Body(...),
    artwork_thumbnail_image_index: Annotated[int, Body()] = None,
    images: Annotated[
        List[UploadFile],
        File(..., description="Разрешены '.webp', '.jpg', '.jpeg', '.png', '.heic'"),
    ] = None,
):
    raise_if_not_image(images)

    ticket_artwork = await TicketsService.create_ticket_artwork(
        uow=uow,
        user=user,
        ticket_artwork_schema=ticket_artwork_schema,
        thumbnail_image_index=artwork_thumbnail_image_index,
        images=images,
    )

    return ticket_artwork


# @router.patch(
#     "/{ticket_artwork_id}",
#     response_model=TicketArtworkReadSchema,
#     description="Даёт возможность изменить поля",
# )
# async def update_ticket_artwork(
#         uow: UOWDep,
#         ticket_artwork_id: int,
#         user: User = Depends(current_user),
#         ticket_artwork_schema: TicketArtworkUpdateSchema = Body(None),
#         thumbnail_image_index: Annotated[int, Body()] = None,
#         images: Annotated[
#             List[UploadFile],
#             File(..., description="Разрешены '.webp', '.jpg', '.jpeg', '.png', '.heic'"),
#         ] = None,
# ):
#     raise_if_not_image(images)
#
#     ticket_artwork = await TicketsService.update_ticket_artwork(
#         uow=uow,
#         ticket_artwork_id=ticket_artwork_id,
#         user=user,
#         ticket_artwork_schema=ticket_artwork_schema,
#         thumbnail_image_index=thumbnail_image_index,
#         images=images,
#     )
#
#     return ticket_artwork


@router.patch(
    "/artwork/approve/{ticket_artwork_id}",
    response_model=TicketArtworkReadSchema,
    description="Подтвердить тикет на добавление арт-объекта. Добавит арт-объект в систему.",
)
async def approve_ticket_artwork(
    uow: UOWDep,
    ticket_artwork_id: int,
    moderator_comment: str = Body(None),
    moderator: Moderator = Depends(get_current_moderator),
):
    try:
        ticket_artwork = await TicketsService.approve_ticket_artwork(
            uow=uow,
            moderator=moderator,
            moderator_comment=moderator_comment,
            ticket_artwork_id=ticket_artwork_id,
        )
    except NoResultFound:
        # Обработка случая, когда объект по классу и id не найден
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=generate_detail(
                error_code=ErrorCode.OBJECT_NOT_FOUND, message="The Object not found"
            ),
        )

    return ticket_artwork


@router.patch(
    "/artwork/reject/{ticket_artwork_id}",
    response_model=TicketArtworkReadSchema,
    description="Отклонить тикет на добавление арт-объекта.",
)
async def reject_ticket_artwork(
    uow: UOWDep,
    ticket_artwork_id: int,
    moderator_comment: str = Body(None),
    moderator: Moderator = Depends(get_current_moderator),
):
    ticket_artwork = await TicketsService.reject_ticket_artwork(
        uow=uow,
        moderator=moderator,
        moderator_comment=moderator_comment,
        ticket_artwork_id=ticket_artwork_id,
    )

    return ticket_artwork
