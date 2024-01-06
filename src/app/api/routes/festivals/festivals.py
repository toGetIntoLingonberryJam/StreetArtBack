from fastapi import APIRouter, HTTPException, Depends
from fastapi_filter import FilterDepends
from fastapi_filter.contrib.sqlalchemy import Filter

from app.api.utils.filters import FestivalFilter
from app.api.utils.paginator import Page, MyParams
from app.modules.festivals.schemas import FestivalRead, FestivalCreate
from app.services.festival import FestivalService
from app.utils.dependencies import UOWDep
from app.utils.exceptions import ObjectNotFoundException

festival_router = APIRouter()


@festival_router.get("/festival/{festival_id}",
                     response_model=FestivalRead,
                     description="Получение фестиваля по id.")
async def get_festival_by_id(uow: UOWDep, festival_id: int):
    try:
        festival = await FestivalService().get_festival_by_id(uow, festival_id)
        return festival
    except ObjectNotFoundException as e:
        raise HTTPException(status_code=404, detail=e.__str__())


@festival_router.post("/",
                      response_model=FestivalRead,
                      description="Создание фестиваля.")
async def create_festival(uow: UOWDep, festival: FestivalCreate):
    festival = await FestivalService().create_festival(uow, festival)
    return festival


@festival_router.get("/",
                     response_model=list[FestivalRead],
                     description="Выводит список фестивалей, использую пагинацию.")
async def get_festival_list(uow: UOWDep,
                            pagination: MyParams = Depends(),
                            filters: Filter = FilterDepends(FestivalFilter)):
    festivals = await FestivalService().get_all_festival(uow, pagination, filters)
    return festivals
