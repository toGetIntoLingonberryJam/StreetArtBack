from typing import Annotated, List, Optional

from fastapi import APIRouter, Body, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from fastapi_cache.decorator import cache
from fastapi_pagination import paginate
from sqlalchemy.exc import NoResultFound

from app.api.routes.common import (
    ErrorCode,
    ErrorModel,
    generate_detail,
    generate_response,
)
from app.api.utils.fastapi_cache import request_key_builder
from app.api.utils.filters.artworks import ArtworkFilter
from app.api.utils.filters.artworks.artwork_location import ArtworkLocationFilter
from app.api.utils.libs.fastapi_filter import FilterDepends
from app.api.utils.libs.fastapi_filter.contrib.sqlalchemy import Filter
from app.api.utils.paginator import MyParams, Page
from app.api.utils.utils import raise_if_not_image, raise_if_not_contains_urls
from app.modules.artworks.schemas.artwork import (
    ArtworkCreateSchema,
    ArtworkReadSchema,
    ArtworkUpdateSchema,
)
from app.modules.artworks.schemas.artwork_card import ArtworkCardSchema
from app.modules.artworks.schemas.artwork_location import ArtworkLocationReadSchema
from app.modules.models import Moderator
from app.modules.users.fastapi_users_config import current_user
from app.modules.users.models import User
from app.services.artworks import ArtworksService
from app.services.collection import CollectionService
from app.utils.dependencies import UOWDep, get_current_moderator
from app.utils.exceptions import ObjectNotFoundException
from app.utils.query_comma_list_support import CommaSeparatedList

router_artworks = APIRouter(tags=["Artworks"])


@router_artworks.get(
    "/locations",
    response_model=list[ArtworkLocationReadSchema],
    description="Выводит список локаций подтверждённых арт-объектов.",
)
@cache(expire=60, namespace="show_artwork_locations", key_builder=request_key_builder)
async def show_artwork_locations(
    uow: UOWDep, filters: Filter = FilterDepends(ArtworkLocationFilter)
):
    # Возвращает локации подтверждённых арт-объектов.
    locations = await ArtworksService().get_artworks_locations(uow, filters)
    return locations


@router_artworks.post(
    path="/",
    response_model=ArtworkReadSchema,
    status_code=status.HTTP_201_CREATED,
    description="ТОЛЬКО ДЛЯ МОДЕРАТОРА. Убрать (После создания арт-объекта, его статус модерации будет 'Ожидает "
    "проверки').",
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
    moderator: Moderator = Depends(get_current_moderator),
    artwork_data: ArtworkCreateSchema = Body(...),
    thumbnail_image_index: Annotated[Optional[int], Body()] = None,
    images: Annotated[
        List[UploadFile],
        File(..., description="Разрешены '.webp', '.jpg', '.jpeg', '.png', '.heic'"),
    ] = None,
    images_urls: Annotated[CommaSeparatedList[str], Body()] = None,
):
    raise_if_not_image(images)
    raise_if_not_contains_urls(images_urls)

    artwork = await ArtworksService().create_artwork(
        uow=uow,
        moderator=moderator,
        artwork_schema=artwork_data,
        images=images,
        images_urls=images_urls,
        thumbnail_image_index=thumbnail_image_index,
    )
    return artwork


# await FastAPICache.clear(namespace="show_artworks")
@router_artworks.get(
    "/",
    response_model=Page[ArtworkCardSchema],
    description=f"""Выводит список подтверждённых арт-объектов, используя пагинацию. Лимит: 50 объектов.\n
    Поля для сортировки: {", ".join(ArtworkFilter.Constants.ordering_model_fields)}\n
    Поля используемые в поиске: {", ".join(ArtworkFilter.Constants.search_model_fields)}""",
)
@cache(expire=60, namespace="show_artworks", key_builder=request_key_builder)
async def show_artworks(
    uow: UOWDep,
    pagination: MyParams = Depends(),
    filters: Filter = FilterDepends(ArtworkFilter),
):
    artworks = await ArtworksService().get_artworks(
        uow=uow, pagination=pagination, filters=filters
    )
    result = paginate(artworks, pagination)
    return result


@router_artworks.get(
    "/{artwork_id}",
    response_model=ArtworkReadSchema,
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
@cache(expire=60, namespace="show_artwork", key_builder=request_key_builder)
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
    response_model=ArtworkReadSchema,
    description="ТОЛЬКО ДЛЯ МОДЕРАТОРОВ! Метод для редактирования отдельных полей арт-объекта.",
    responses={
        status.HTTP_404_NOT_FOUND: generate_response(
            error_model=ErrorModel,
            error_code=ErrorCode.OBJECT_NOT_FOUND,
            summary="Object not found",
            message="Artwork not found",
        )
    },
)
async def update_artwork(
    artwork_id: int,
    artwork_data: ArtworkUpdateSchema,
    uow: UOWDep,
    moderator: Moderator = Depends(get_current_moderator),
):
    try:
        artwork = await ArtworksService().update_artwork(uow, artwork_id, artwork_data)
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
    description="ТОЛЬКО ДЛЯ МОДЕРАТОРА! Удаляет арт-объект и его связные сущности, включая изображения.",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: generate_response(
            error_model=ErrorModel,
            error_code=ErrorCode.OBJECT_NOT_FOUND,
            summary="Object not found",
            message="Artwork not found",
        )
    },
)
async def delete_artwork(
    artwork_id: int, uow: UOWDep, moderator: Moderator = Depends(get_current_moderator)
):
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
    "/{artwork_id}/switch_like",
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
async def switch_like(artwork_id: int, uow: UOWDep, user: User = Depends(current_user)):
    try:
        artwork = await ArtworksService().get_artwork(uow, artwork_id)
        reaction_add = await CollectionService().toggle_artwork_like(
            uow, user.id, artwork.id
        )
        return reaction_add
    except ObjectNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=generate_detail(
                error_code=ErrorCode.OBJECT_NOT_FOUND, message=e.__str__()
            ),
        )
