from enum import Enum
from typing import Tuple, Optional

import polyline
import requests

from app.api.utils.libs.fastapi_filter.contrib.sqlalchemy import Filter
from app.services.artworks import ArtworksService
from app.utils.unit_of_work import UnitOfWork


class TransportationMode(Enum):
    CAR = "car"
    BIKE = "bike"
    FOOT = "foot"


class GeoService:
    @staticmethod
    async def get_route(
        uow: UnitOfWork,
        geo_artwork_filter: Filter,
        mode: TransportationMode,
        user_coords: Optional[Tuple[float, float]] = None,
    ):
        """Метод отправляет запрос к OSRM server'у и парсит JSON-ответ для получения дистанции, продолжительности и
        информации о передвижении. Возвращает словарь"""
        artworks = await ArtworksService.get_artworks(
            uow=uow, filters=geo_artwork_filter
        )

        if not user_coords and len(artworks) <= 1:
            raise ValueError(
                "Less than two values were passed. It is necessary to specify the coordinates of the user and "
                "the art object/s, or more than one art object."
            )

        coordinates = [
            (artwork.location.latitude, artwork.location.longitude)
            for artwork in artworks
        ]
        if user_coords:
            coordinates = [tuple(user_coords)] + coordinates

        polyline_coords = polyline.encode(coordinates=coordinates)

        url = (
            f"https://routing.openstreetmap.de/routed-{mode.value}/route/v1/driving/"
            + f"polyline({polyline_coords})"
        )

        response = requests.get(url)
        if response.status_code != 200:
            response.raise_for_status()

        res = response.json()
        routes = polyline.decode(res["routes"][0]["geometry"])
        # start_point = [
        #     res["waypoints"][0]["location"][1],
        #     res["waypoints"][0]["location"][0],
        # ]
        # end_point = [
        #     res["waypoints"][1]["location"][1],
        #     res["waypoints"][1]["location"][0],
        # ]
        waypoints = [point["location"] for point in res["waypoints"]]

        distance = res["routes"][0]["distance"]
        duration = res["routes"][0]["duration"]

        out = {
            "route": routes,  # a list of tuples of coordinates along the route
            "waypoints": waypoints,  # list of float coords
            # "start_point": start_point,
            # "end_point": end_point,
            "distance": distance,  # in metres
            "duration": duration,  # in seconds
        }

        return out
