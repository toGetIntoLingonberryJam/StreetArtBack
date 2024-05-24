from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi_pagination import paginate
from starlette import status

from app.api.routes.common import (
    ErrorCode,
    ErrorModel,
    generate_detail,
    generate_response,
)
from app.api.utils.filters.artists.artist import ArtistFilter
from app.api.utils.libs.fastapi_filter import FilterDepends
from app.api.utils.libs.fastapi_filter.contrib.sqlalchemy import Filter
from app.api.utils.paginator import MyParams, Page
from app.modules.artists.schemas.artist import ArtistCreateSchema, ArtistReadSchema
from app.api.utils.utils import is_image
from app.modules import User, Moderator
from app.modules.artists.schemas.artist_card import ArtistCardSchema
from app.modules.artworks.schemas.artwork_card import ArtworkCardSchema
from app.modules.users.fastapi_users_config import current_user
from app.services.artist import ArtistsService
from app.services.artworks import ArtworksService
from app.services.collection import CollectionService
from app.utils.dependencies import UOWDep, get_current_moderator
from app.utils.exceptions import (
    IncorrectInput,
    ObjectNotFoundException,
    UserNotFoundException,
)

artist_router = APIRouter(prefix="/artists", tags=["Artist"])


@artist_router.get(
    "/{artist_id}",
    response_model=ArtistReadSchema,
    description="Получение артиста по id",
    responses={
        status.HTTP_404_NOT_FOUND: generate_response(
            error_model=ErrorModel,
            error_code=ErrorCode.OBJECT_NOT_FOUND,
            summary="Object not found",
            message="Artist not found",
        )
    },
)
async def get_artist(artist_id: int, uow: UOWDep):
    try:
        artist = await ArtistsService().get_artist_by_id(uow, artist_id)
        return artist
    except ObjectNotFoundException as e:
        raise HTTPException(status_code=404, detail=e.__str__())


@artist_router.post(
    "/",
    response_model=ArtistReadSchema,
    description="Создание артиста",
    responses={
        status.HTTP_404_NOT_FOUND: generate_response(
            error_model=ErrorModel,
            error_code=ErrorCode.OBJECT_NOT_FOUND,
            summary="Object not found",
            message="User not found",
        )
    },
)
async def create_artist(
        artist: ArtistCreateSchema,
        uow: UOWDep,
        image: Annotated[
            UploadFile, File(..., description="Изображение в формате jpeg, png или heic.")
        ] = None,
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
    try:
        artist = await ArtistsService().create_artist(uow, artist, image)
    except UserNotFoundException:
        raise HTTPException(status_code=404)
    except IncorrectInput as e:
        raise HTTPException(status_code=400, detail=e.__str__())
    return artist


@artist_router.get(
    "/", response_model=Page[ArtistCardSchema], description="Получение списка артистов"
)
async def get_artist_list(
        uow: UOWDep,
        pagination: MyParams = Depends(),
        filters: Filter = FilterDepends(ArtistFilter),
):
    artists = await ArtistsService().get_all_artist(uow, pagination, filters)
    return paginate(artists, pagination)


@artist_router.get(
    "/{artist_id}/artworks",
    response_model=Page[ArtworkCardSchema],
    description="Получение списка работ художника по id",
)
async def get_artist_artworks(
        uow: UOWDep, artist_id: int, pagination: MyParams = Depends()
):
    artworks = await ArtworksService().get_approved_artworks(
        uow, pagination, artist_id=artist_id
    )
    return paginate(artworks, pagination)


@artist_router.post(
    "/assignee",
    response_model=ArtworkCardSchema,
    description="Присвоение художнику работы.",
)
async def assignee_artwork(uow: UOWDep,
                           artwork_id: int,
                           artist_id: int,
                           moderator: Moderator = Depends(get_current_moderator)):
    try:
        artwork = await ArtistsService().update_artwork_artist(uow, artwork_id, artist_id)
        return artwork
    except ObjectNotFoundException as e:
        raise HTTPException(status_code=404, detail=e.__str__())


@artist_router.post(
    "/unassignee",
    response_model=ArtworkCardSchema,
    description="Отмена присвоения художнику работы.",
)
async def unassignee_artwork(uow: UOWDep,
                             artwork_id: int,
                             artist_id: int,
                             moderator: Moderator = Depends(get_current_moderator)):
    try:
        artwork = await ArtistsService().remove_artwork_artist(
            uow, artwork_id, artist_id
        )
        return artwork
    except ObjectNotFoundException as e:
        raise HTTPException(status_code=404, detail=e.__str__())


@artist_router.post(
    "/{artist_id}/switch_like",
    description="Ставит и удаляет лайк на художника.",
    responses={
        status.HTTP_404_NOT_FOUND: generate_response(
            error_model=ErrorModel,
            error_code=ErrorCode.OBJECT_NOT_FOUND,
            summary="Object not found",
            message="Artist not found",
        )
    },
)
async def switch_like(artist_id: int, uow: UOWDep, user: User = Depends(current_user)):
    try:
        artist = await ArtistsService().get_artist_by_id(uow, artist_id)
        reaction_add = await CollectionService().toggle_artist_like(
            uow, user.id, artist.id
        )
        return reaction_add
    except ObjectNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=generate_detail(
                error_code=ErrorCode.OBJECT_NOT_FOUND, message=e.__str__()
            ),
        )
