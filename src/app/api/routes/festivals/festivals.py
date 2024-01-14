from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from starlette import status

from app.api.routes.common import (
    generate_response,
    ErrorModel,
    ErrorCode,
    generate_detail,
)
from app.api.utils import is_image
from app.api.utils.libs.fastapi_filter import FilterDepends
from app.api.utils.libs.fastapi_filter.contrib.sqlalchemy import Filter
from fastapi_pagination import paginate

from app.api.utils.filters.festivals.festival import FestivalFilter
from app.api.utils.paginator import Page, MyParams
from app.modules import User
from app.modules.artworks.schemas.artwork_card import ArtworkCardSchema
from app.modules.festivals.schemas import FestivalReadSchema, FestivalCreateSchema
from app.modules.users.fastapi_users_config import current_user
from app.services.artist import ArtistsService
from app.services.artworks import ArtworksService
from app.services.collection import CollectionService
from app.services.festival import FestivalService
from app.utils.dependencies import UOWDep
from app.utils.exceptions import ObjectNotFoundException

festival_router = APIRouter()


@festival_router.get(
    "/festival/{festival_id}",
    response_model=FestivalReadSchema,
    description="Получение фестиваля по id.",
)
async def get_festival_by_id(uow: UOWDep, festival_id: int):
    try:
        festival = await FestivalService().get_festival_by_id(uow, festival_id)
        return festival
    except ObjectNotFoundException as e:
        raise HTTPException(status_code=404, detail=e.__str__())


@festival_router.post(
    "/",
    response_model=FestivalReadSchema,
    description="Создание фестиваля."
)
async def create_festival(uow: UOWDep,
                          festival: FestivalCreateSchema,
                          image: Annotated[
                              UploadFile,
                              File(..., description="Изображение в формате jpeg, png или heic.")
                          ] = None
                          ):
    if image and not is_image(image):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=generate_detail(
                error_code=ErrorCode.INVALID_IMAGE_FILE_EXTENSION,
                message="Invalid image file extension",
                data={"filename": image.filename},
            ),
        )
    festival = await FestivalService().create_festival(uow, festival, image)
    return festival


@festival_router.get(
    "/",
    response_model=Page[FestivalReadSchema],
    description="Выводит список фестивалей, использую пагинацию.",
)
async def get_festival_list(
        uow: UOWDep,
        pagination: MyParams = Depends(),
        filters: Filter = FilterDepends(FestivalFilter),
):
    festivals = await FestivalService().get_all_festival(uow, pagination, filters)
    return paginate(festivals, pagination)


@festival_router.post(
    "/assignee",
    response_model=ArtworkCardSchema,
    description="Присвоение фестивалю работы.",
)
async def assignee_artwork(uow: UOWDep, artwork_id: int, artist_id: int):
    try:
        artwork = await FestivalService().update_artwork_festival(
            uow, artwork_id, artist_id
        )
        return artwork
    except ObjectNotFoundException as e:
        raise HTTPException(status_code=404, detail=e.__str__())


@festival_router.get(
    "/{festival_id}/artworks",
    response_model=Page[ArtworkCardSchema],
    description="Получение списка работ фестиваля по id",
)
async def get_festival_artworks(
        uow: UOWDep, festival_id: int, pagination: MyParams = Depends()
):
    artworks = await ArtworksService().get_approved_artworks(
        uow, pagination, festival_id=festival_id
    )
    return paginate(artworks, pagination)


@festival_router.post(
    "/{festival_id}/toggle_like",
    description="Ставит и удаляет лайк на фестиваль.",
    responses={
        status.HTTP_404_NOT_FOUND: generate_response(
            error_model=ErrorModel,
            error_code=ErrorCode.OBJECT_NOT_FOUND,
            summary="Object not found",
            message="Festival not found",
        )
    },
)
async def toggle_like(
        festival_id: int, uow: UOWDep, user: User = Depends(current_user)
):
    try:
        festival = await FestivalService().get_festival_by_id(uow, festival_id)
        reaction_add = await CollectionService().toggle_festival_like(
            uow, user.id, festival.id
        )
        return reaction_add
    except ObjectNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=generate_detail(
                error_code=ErrorCode.OBJECT_NOT_FOUND, message=e.__str__()
            ),
        )
