from typing import List, Tuple

from pydantic import BaseModel, confloat


class RouteReadSchema(BaseModel):
    waypoints: List[Tuple[float, float]]
    # start_point: List[float]
    # end_point: List[float]
    distance: confloat(ge=0)
    duration: confloat(ge=0)
    route: List[Tuple[float, float]]
