from fastapi import APIRouter, HTTPException, Depends
from app.api.utils.libs.fastapi_filter import FilterDepends
from app.api.utils.libs.fastapi_filter.contrib.sqlalchemy import Filter
from fastapi_pagination import paginate

from app.api.routes.artists.artists import artist_router
from app.api.utils.filters.festivals.festival import FestivalFilter
from app.api.utils.paginator import Page, MyParams
from app.modules.artworks.schemas.artwork_card import ArtworkCardSchema
from app.modules.festivals.schemas import FestivalReadSchema, FestivalCreateSchema
from app.services.artist import ArtistsService
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
    "/", response_model=FestivalReadSchema, description="Создание фестиваля."
)
async def create_festival(uow: UOWDep, festival: FestivalCreateSchema):
    festival = await FestivalService().create_festival(uow, festival)
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


@artist_router.post(
    "/assignee",
    response_model=ArtworkCardSchema,
    description="Присвоение художнику работы.",
)
async def assignee_artwork(uow: UOWDep, artwork_id: int, artist_id: int):
    try:
        artwork = await ArtistsService().update_artwork_artist(
            uow, artwork_id, artist_id
        )
        return artwork
    except ObjectNotFoundException as e:
        raise HTTPException(status_code=404, detail=e.__str__())
