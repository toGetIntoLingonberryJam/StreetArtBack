import imghdr
from typing import Annotated, List

from fastapi import APIRouter, UploadFile, HTTPException, File, Body
from fastapi.responses import JSONResponse
from sqlalchemy.exc import NoResultFound

from app.modules.artworks.schemas.artwork import ArtworkCreate, Artwork, ArtworkEdit
from app.modules.artworks.schemas.artwork_location import ArtworkLocation
from app.services.artworks import ArtworksService
from app.utils.dependencies import UOWDep

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


@router_artworks.post("/create/", response_model=Artwork)
async def create_artwork(uow: UOWDep,
                         artwork_data: ArtworkCreate = Body(...),
                         thumbnail_image_index: Annotated[int, Body()] = None,
                         images: Annotated[List[UploadFile],
                         File(..., description="Разрешены '.jpg', '.jpeg', '.png', '.heic'")] = None):
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
    try:
        artwork = await ArtworksService().get_artwork(uow, artwork_id)
        return artwork
    except NoResultFound:
        # Обработка случая, когда запись не найдена
        # Вернуть 404 ошибку или пустой объект
        return JSONResponse(content={"message": "Artwork not found"}, status_code=404)
    except Exception as e:
        # Обработка других ошибок, если они возникают
        # Вернуть 500 ошибку или другое сообщение об ошибке
        return JSONResponse(content={"message": "Internal Server Error"}, status_code=500)


@router_artworks.patch("/edit/{artwork_id}", response_model=Artwork)
async def edit_artwork(artwork_id: int, artwork_data: ArtworkEdit, uow: UOWDep):
    try:
        artwork = await ArtworksService().edit_artwork(uow, artwork_id, artwork_data)
        return artwork
    except NoResultFound:
        # Обработка случая, когда запись не найдена
        # Вернуть 404 ошибку или пустой объект
        return JSONResponse(content={"message": "Artwork not found"}, status_code=404)
    except Exception as e:
        # Обработка других ошибок, если они возникают
        # Вернуть 500 ошибку или другое сообщение об ошибке
        return JSONResponse(content={"message": "Internal Server Error"}, status_code=500)


@router_artworks.delete("/delete/{artwork_id}")
async def delete_artwork(artwork_id: int, uow: UOWDep):
    # try:
    await ArtworksService().delete_artwork(uow, artwork_id)
    # return {"message": "Object deleted successfully"}
    # except ObjectNotFound as exc:
    #     raise exc


@router_artworks.get('/show/locations/', response_model=list[ArtworkLocation])
async def show_artwork_locations(uow: UOWDep):
    # Возвращает локации арт-объектов, если местоположение не указано - выведено не будет.
    locations = await ArtworksService().get_artworks_locations(uow)
    return locations
