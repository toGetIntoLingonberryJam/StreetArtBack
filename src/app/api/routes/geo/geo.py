from typing import Optional, List, Tuple, Annotated

from fastapi import APIRouter, Query, HTTPException, status
from requests import HTTPError

from app.api.routes.common import (
    ErrorModel,
    ErrorCode,
    generate_response,
    generate_detail,
)
from app.api.utils.filters.geo.artwork import GeoArtworkFilter
from app.api.utils.libs.fastapi_filter import FilterDepends
from app.api.utils.libs.fastapi_filter.contrib.sqlalchemy import Filter
from app.modules.geo.schemas.route import RouteReadSchema
from app.services.geo import GeoService, TransportationMode
from app.utils.dependencies import UOWDep
from app.utils.query_comma_list_support import CommaSeparatedList

router = APIRouter(tags=["Geo"])


@router.get(
    "/route",
    response_model=RouteReadSchema,
    description="""Просчитывает путь от одного арт-объекта до другого.\nПример перечисления ID арт-объектов:\n?artwork_ids=1,2,3""",
    responses={
        status.HTTP_504_GATEWAY_TIMEOUT: generate_response(
            error_model=ErrorModel,
            error_code=ErrorCode.GATEWAY_TIMEOUT,
            summary="The external server is not responding",
            message="Couldn't get a route from an external server",
        ),
        status.HTTP_400_BAD_REQUEST: generate_response(
            error_model=ErrorModel,
            error_code=ErrorCode.INCORRECT_ROUTE_COORDINATES,
            summary="specify the coordinates of the user and the art object/s, or more than one art object.",
            message="Less than two values were passed. It is necessary to specify the coordinates of the user and "
            "the art object/s, or more than one art object.",
        ),
    },
)
# @cache(expire=15)
async def show_artwork_locations(
    uow: UOWDep,
    filters: Filter = FilterDepends(GeoArtworkFilter),
    transportation_mode: TransportationMode = TransportationMode.FOOT,
    user_coords: Annotated[
        CommaSeparatedList[float] | None,
        Query(description="Ожидаются float-значения: Ширина, Долгота"),
    ] = None
    # user_coords: Optional[Tuple[float, float]] = Query(
    #     None, description="Ожидаются float-значения: Ширина, Долгота"
    # ), #TODO: Не работает.
):
    try:
        route = await GeoService.get_route(
            uow=uow,
            geo_artwork_filter=filters,
            mode=transportation_mode,
            user_coords=user_coords,
        )
        return route
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUESTHT,
            detail=generate_detail(ErrorCode.GATEWAY_TIMEOUT, message=str(e)),
        )
    except HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=generate_detail(
                ErrorCode.GATEWAY_TIMEOUT,
                message="Couldn't get a route from an external server",
            ),
        )
