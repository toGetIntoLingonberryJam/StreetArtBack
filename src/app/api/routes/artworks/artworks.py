from typing import Annotated, List

from fastapi import APIRouter, UploadFile, HTTPException, File, Body, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.exc import NoResultFound

from app.api.utils import is_image
from app.modules.artworks.schemas.artwork import ArtworkCreate, Artwork, ArtworkEdit, ArtworkForModerator
from app.modules.artworks.schemas.artwork_location import ArtworkLocation
from app.modules.users.fastapi_users_config import current_user
from app.modules.users.models import User
from app.services.artworks import ArtworksService
from app.utils.dependencies import UOWDep

router_artworks = APIRouter(tags=["Artworks"])


@router_artworks.get("/locations", response_model=list[ArtworkLocation],
                     description="Выводит список локаций подтверждённых арт-объектов.")
# @cache(expire=15)
async def show_artwork_locations(uow: UOWDep):
    # Возвращает локации арт-объектов, если местоположение не указано - выведено не будет.
    locations = await ArtworksService().get_artworks_locations(uow)
    return locations


@router_artworks.post(path="/", response_model=Artwork,
                      description="После создания арт-объекта, его статус модерации будет 'Ожидает проверки'.")
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
                    status_code=400, detail=f"Invalid image file extension {image.filename}"
                )

    artwork = await ArtworksService().create_artwork(
        uow=uow, user=user, artwork_schem=artwork_data, images=images, thumbnail_image_index=thumbnail_image_index
    )

    # artwork_images = await ArtworksService().

    return artwork


# @cache(expire=60, namespace="show_artworks")
# await FastAPICache.clear(namespace="show_artworks")
@router_artworks.get("/", response_model=list[Artwork],
                     description="Выводит список арт-объектов, используя пагинацию. Лимит: 50 объектов.")
async def show_artworks(uow: UOWDep, offset: int = 0, limit: int = 20):
    limit = min(max(limit, 1), 50)  # Ограничение в минимум 1 и максимум 50 арт-объектов за раз.

    artworks = await ArtworksService().get_approved_artworks(uow, offset=offset, limit=limit)

    return artworks


@router_artworks.get("/{artwork_id}", response_model=Artwork,
                     description="Выводит арт-объект по его ID.")
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
        return JSONResponse(
            content={"message": "Internal Server Error"}, status_code=500
        )


@router_artworks.patch("/{artwork_id}", response_model=ArtworkForModerator,
                       description="Метод для редактирования отдельных полей арт-объекта.")
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
        return JSONResponse(
            content={"message": "Internal Server Error"}, status_code=500
        )


# ToDO: доработать метод удаления. Возвращает мало информации + нет response_model.
@router_artworks.delete("/{artwork_id}",
                        description="Удаляет арт-объект и его связные сущности, включая изображения.")
async def delete_artwork(artwork_id: int, uow: UOWDep,):
    try:
        await ArtworksService().delete_artwork(uow, artwork_id)
        return JSONResponse(content={"message": "Object deleted successfully"}, status_code=200)
    except NoResultFound:
        # Обработка случая, когда запись не найдена
        # Вернуть 404 ошибку или пустой объект
        return JSONResponse(content={"message": "Artwork not found"}, status_code=404)
    # except ObjectNotFound as exc:
    #     raise exc


