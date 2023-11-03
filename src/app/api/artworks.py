from typing import List, Annotated, Any

from fastapi import APIRouter, UploadFile, File, Body, HTTPException
from fastapi.params import Form

import imghdr

from pydantic import Json

from app.modules.artworks.schemas.artwork_location import ArtworkLocation
from app.utils.dependencies import UOWDep
from app.modules.artworks.schemas.artwork import ArtworkCreate, Artwork, ArtworkEdit
from app.services.artworks import ArtworksService

router_artworks = APIRouter(prefix="/artwork", tags=["artwork"])


def is_image(file: UploadFile) -> bool:
    allowed_extensions = {"jpg", "jpeg", "png", "heic"}  # Расширения файлов изображений, которые разрешены
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in allowed_extensions:
        return False

    # Если расширение файла соответствует изображению, дополнительно проверяем его содержимое
    content = file.file.read(1024)  # Считываем первые 1024 байта для определения типа содержимого
    image_type = imghdr.what(None, h=content)

    return image_type is not None


class JsonForm(Json[Any], Form):
    ...


@router_artworks.post("/create/", response_model=Artwork)
async def create_artwork(uow: UOWDep,
                         artwork_data: ArtworkCreate = Body(...),
                         thumbnail_image_index: Annotated[int, Body()] = None,
                         images: Annotated[List[UploadFile], File(...,
                                                                        description="Разрешены '.jpg', '.jpeg', '.png', '.heic'")] = None):
    if images:
        for image in images:
            if not is_image(image):
                raise HTTPException(status_code=400, detail=f"Invalid image file {image.filename}")

    # artwork_data = ArtworkCreate(**artwork_data)
    artwork = await ArtworksService().create_artwork(uow, artwork_data, images=images,
                                                     thumbnail_image_index=thumbnail_image_index)

    # artwork_images = await ArtworksService().

    return artwork


@router_artworks.get("/show/", response_model=list[Artwork])
async def show_artworks(uow: UOWDep):
    artworks = await ArtworksService().get_artworks(uow)
    return artworks


@router_artworks.get("/show/{artwork_id}", response_model=Artwork)
async def show_artwork(artwork_id: int, uow: UOWDep):
    artwork = await ArtworksService().get_artwork(uow, artwork_id)
    return artwork


@router_artworks.patch("/edit/{artwork_id}", response_model=Artwork)
async def edit_artwork(artwork_id: int, artwork_data: ArtworkEdit, uow: UOWDep):
    artwork = await ArtworksService().edit_artwork(uow, artwork_id, artwork_data)
    return artwork


@router_artworks.delete("/delete/{artwork_id}")
async def delete_artwork(artwork_id: int, uow: UOWDep):
    # try:
    await ArtworksService().delete_artwork(uow, artwork_id)
    # return {"message": "Object deleted successfully"}
    # except ObjectNotFound as exc:
    #     raise exc


@router_artworks.get('/locations/show/', response_model=list[ArtworkLocation])
async def show_artwork_locations(uow: UOWDep):
    # Возвращает локации арт-объектов, если местоположение не указано - выведено не будет.
    locations = await ArtworksService().get_artworks_locations(uow)
    return locations
