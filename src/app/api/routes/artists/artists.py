from typing import List

from fastapi import APIRouter, HTTPException
from starlette import status

from app.api.routes.common import generate_response, ErrorModel, ErrorCode
from app.modules.artists.schemas import ArtistRead, ArtistCreate
from app.modules.artworks.schemas.artwork import Artwork
from app.services.artist import ArtistsService
from app.utils.dependencies import UOWDep
from app.utils.exceptions import UserNotFoundException, IncorrectInput, ObjectNotFoundException

artist_router = APIRouter(prefix="/artists", tags=["artist"])


@artist_router.get("/{artist_id}",
                   response_model=ArtistRead,
                   description="Получение артиста по id",
                   responses={status.HTTP_404_NOT_FOUND: generate_response(
                       error_model=ErrorModel,
                       error_code=ErrorCode.OBJECT_NOT_FOUND,
                       summary="Object not found",
                       message="Artist not found",
                   )})
async def get_artist(artist_id: int, uow: UOWDep):
    artist = await ArtistsService().get_artist_by_id(uow, artist_id)
    if not artist:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return artist


@artist_router.post("/",
                    response_model=ArtistRead,
                    description="Создание артиста",
                    responses={status.HTTP_404_NOT_FOUND: generate_response(
                        error_model=ErrorModel,
                        error_code=ErrorCode.OBJECT_NOT_FOUND,
                        summary="Object not found",
                        message="User not found",
                    )})
async def get_artist(artist: ArtistCreate, uow: UOWDep):
    try:
        artist = await ArtistsService().create_artist(uow, artist)
    except UserNotFoundException:
        raise HTTPException(status_code=404)
    except IncorrectInput as e:
        raise HTTPException(status_code=400, detail=e.__str__())
    return artist


@artist_router.get("/",
                   response_model=List[ArtistRead],
                   description="Получение списка артистов")
async def get_artist(uow: UOWDep, limit: int = 0, offset: int | None = None):
    artists = await ArtistsService().get_all_artist(uow, offset, limit)
    return artists


@artist_router.post("/assignee",
                    response_model=Artwork,
                    description="Присвоение художнику работы.")
async def assignee_artwork(uow: UOWDep, artwork_id: int, artist_id: int):
    try:
        artwork = await ArtistsService().update_artwork_artist(uow, artwork_id, artist_id)
        return Artwork.model_validate(artwork)
    except ObjectNotFoundException as e:
        raise HTTPException(status_code=404, detail=e.__str__())
