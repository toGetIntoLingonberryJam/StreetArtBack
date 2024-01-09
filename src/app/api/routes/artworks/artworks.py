from typing import Annotated, List

from fastapi import APIRouter, UploadFile, HTTPException, File, Body, Depends, status
from fastapi.responses import JSONResponse
from fastapi_filter import FilterDepends
from fastapi_filter.contrib.sqlalchemy import Filter
from sqlalchemy.exc import NoResultFound

from app.api.routes.common import (
    ErrorModel,
    ErrorCode,
    generate_response,
    generate_detail,
)
from app.api.utils import is_image
from app.api.utils.filters import ArtworkFilter
from app.api.utils.paginator import Page, MyParams
from fastapi_pagination import paginate

from app.modules.artworks.schemas.artwork import (
    ArtworkCreate,
    Artwork,
    ArtworkEdit,
    ArtworkForModerator,
)
from app.modules.artworks.schemas.artwork_location import ArtworkLocation
from app.modules.users.fastapi_users_config import current_user
from app.modules.users.models import User
from app.services.artworks import ArtworksService
from app.services.user import UserService
from app.utils.dependencies import UOWDep

router_artworks = APIRouter(tags=["Artworks"])


# Page = Page.with_custom_options(
#     size=Query(20, ge=1, le=50),
# )


@router_artworks.get(
    "/locations",
    response_model=list[ArtworkLocation],
    description="Выводит список локаций подтверждённых арт-объектов.",
)
# @cache(expire=15)
async def show_artwork_locations(uow: UOWDep):
    # Возвращает локации подтверждённых арт-объектов.
    locations = await ArtworksService().get_artworks_locations(uow)
    return locations


@router_artworks.post(
    path="/",
    response_model=Artwork,
    status_code=status.HTTP_201_CREATED,
    description="После создания арт-объекта, его статус модерации будет 'Ожидает проверки'.",
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
async def create_artwork(
    uow: UOWDep,
    user: User = Depends(current_user),
    artwork_data: ArtworkCreate = Body(...),
    thumbnail_image_index: Annotated[int, Body()] = None,
    images: Annotated[
        List[UploadFile],
        File(..., description="Разрешены '.jpg', '.jpeg', '.png', '.heic'"),
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

    artwork = await ArtworksService().create_artwork(
        uow=uow,
        user=user,
        artwork_schem=artwork_data,
        images=images,
        thumbnail_image_index=thumbnail_image_index,
    )

    # artwork_images = await ArtworksService().

    return artwork


# @cache(expire=60, namespace="show_artworks")
# await FastAPICache.clear(namespace="show_artworks")
@router_artworks.get(
    "/",
    response_model=Page[Artwork],
    description="Выводит список подтверждённых арт-объектов, используя пагинацию. Лимит: 50 объектов.",
)
async def show_artworks(
    uow: UOWDep,
    pagination: MyParams = Depends(),
    filters: Filter = FilterDepends(ArtworkFilter),
):
    artworks = await ArtworksService().get_approved_artworks(uow, pagination, filters)
    return paginate(artworks, pagination)


@router_artworks.get(
    "/{artwork_id}",
    response_model=Artwork,
    description="Выводит арт-объект по его ID.",
    responses={
        status.HTTP_404_NOT_FOUND: generate_response(
            error_model=ErrorModel,
            error_code=ErrorCode.OBJECT_NOT_FOUND,
            summary="Object not found",
            message="Artwork not found",
        )
    },
)
async def show_artwork(artwork_id: int, uow: UOWDep):
    try:
        artwork = await ArtworksService().get_artwork(uow, artwork_id)
        return artwork
    except NoResultFound:
        # Обработка случая, когда запись не найдена
        # Вернуть 404 ошибку или пустой объект
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=generate_detail(
                error_code=ErrorCode.OBJECT_NOT_FOUND, message="Artwork not found"
            ),
        )


@router_artworks.patch(
    "/{artwork_id}",
    response_model=ArtworkForModerator,
    description="Метод для редактирования отдельных полей арт-объекта.",
    responses={
        status.HTTP_404_NOT_FOUND: generate_response(
            error_model=ErrorModel,
            error_code=ErrorCode.OBJECT_NOT_FOUND,
            summary="Object not found",
            message="Artwork not found",
        )
    },
)
async def edit_artwork(artwork_id: int, artwork_data: ArtworkEdit, uow: UOWDep):
    try:
        artwork = await ArtworksService().edit_artwork(uow, artwork_id, artwork_data)
        return artwork
    except NoResultFound:
        # Обработка случая, когда запись не найдена
        # Вернуть 404 ошибку или пустой объект
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=generate_detail(
                error_code=ErrorCode.OBJECT_NOT_FOUND, message="Artwork not found"
            ),
        )


# ToDO: доработать метод удаления. Возвращает мало информации + нет response_model.
@router_artworks.delete(
    "/{artwork_id}",
    description="Удаляет арт-объект и его связные сущности, включая изображения.",
    responses={
        status.HTTP_404_NOT_FOUND: generate_response(
            error_model=ErrorModel,
            error_code=ErrorCode.OBJECT_NOT_FOUND,
            summary="Object not found",
            message="Artwork not found",
        )
    },
)
async def delete_artwork(artwork_id: int, uow: UOWDep):
    try:
        await ArtworksService().delete_artwork(uow, artwork_id)
        return JSONResponse(
            content={"message": "Object deleted successfully"},
            status_code=status.HTTP_200_OK,
        )
    except NoResultFound:
        # Обработка случая, когда запись не найдена
        # Вернуть 404 ошибку или пустой объект
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=generate_detail(
                error_code=ErrorCode.OBJECT_NOT_FOUND, message="Artwork not found"
            ),
        )
    # except ObjectNotFound as exc:
    #     raise exc


@router_artworks.post(
    "/{artwork_id}/toggle_like",
    description="Ставит и удаляет лайк на арт-объект.",
    responses={
        status.HTTP_404_NOT_FOUND: generate_response(
            error_model=ErrorModel,
            error_code=ErrorCode.OBJECT_NOT_FOUND,
            summary="Object not found",
            message="Artwork not found",
        )
    },
)
async def toggle_like(artwork_id: int, uow: UOWDep, user: User = Depends(current_user)):
    try:
        artwork = await ArtworksService().get_artwork(uow, artwork_id)
        reaction = await UserService().make_reaction(uow, user.id, artwork.id)
        return True if reaction else False
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=generate_detail(
                error_code=ErrorCode.OBJECT_NOT_FOUND, message="Artwork not found"
            ),
        )
