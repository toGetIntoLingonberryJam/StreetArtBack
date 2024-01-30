import asyncio
import csv
import json
from typing import List

import requests
from pydantic import BaseModel, HttpUrl


class ArtworkData(BaseModel):
    title: str
    year_created: int
    festival: str
    description: str
    image_urls: List[HttpUrl]
    artist_name: str
    links: List[HttpUrl]
    latitude: float
    longitude: float
    address: str


def read_data_from_table(table_name) -> List[ArtworkData]:
    artworks = []
    with open(table_name, "r", encoding="utf-8") as file:
        # Create a CSV reader object
        reader = csv.reader(file)

        # Skip the header row
        next(reader)

        # Iterate over each row in the CSV file
        for row in reader:
            # Process the data in each row
            # For example, print the values in each row
            latitude, longitude = map(float, [i.strip("°") for i in row[8].split()])
            images = [HttpUrl(url) for url in row[10].split()]
            links = [HttpUrl(url) for url in row[4].split()]
            artwork = ArtworkData(
                title=row[0],
                year_created=int(row[1]),
                festival=row[2],
                description=row[3],
                artist_name=row[5],
                address=row[9],
                longitude=longitude,
                latitude=latitude,
                image_urls=images,
                links=links,
            )
            artworks.append(artwork)
    return artworks


auth_data = {"username": "tyler565688@gmail.com", "password": "string"}


async def create_artwork(
    artwork: ArtworkData, url: str, header: dict, urls: List[HttpUrl]
):
    artwork_schema = {
        "title": artwork.title,
        "year_created": artwork.year_created,
        "description": artwork.description,
        "festival_id": None,
        "artist_id": None,
        "status": "existing",
        "links": [i.__str__() for i in artwork.links],
        "location": {
            "latitude": artwork.latitude,
            "longitude": artwork.longitude,
            "address": artwork.address,
        },
    }
    header.update({"accept": "application/json"})

    artwork_data_str = json.dumps(artwork_schema, ensure_ascii=False)

    files = {"artwork_data": (None, artwork_data_str)}
    params = {"images_urls": [i.__str__() for i in artwork.image_urls]}

    response = requests.post(
        url + "/v1/artworks", headers=header, files=files, params=params
    )

    print(response.text)

    return response.json()


async def create_auth_token(url: str, auth_data: dict):
    response = requests.post(url + "/v1/auth/login", data=auth_data)

    token = response.json()["access_token"]
    return token


def get_current_artist(artist_name, url, header):
    data = {"search": artist_name, "page": 1, "size": 1}
    response = requests.get(url + "/v1/artists", headers=header, data=data)
    artists = response.json()

    for artist in artists["items"]:
        if artist["name"] == artist_name:
            return artist


def assignee_artist(artwork_id, artist_id, url, header):
    data = {"artwork_id": artwork_id, "artist_id": artist_id}
    response = requests.post(url + "/v1/artists/assignee", headers=header, params=data)
    return response


def create_artist(name, url, header):
    data = {"name": name, "description": ""}
    header.update({"accept": "application/json"})

    data_str = json.dumps(data, ensure_ascii=False)

    files = {"artist": (None, data_str)}
    response = requests.post(url + "/v1/artists", headers=header, files=files)
    return response.json()


def get_current_festival(festival_name, url, header):
    data = {"search": festival_name, "page": 1, "size": 1}
    response = requests.get(url + "/v1/festivals", headers=header, data=data)
    festivals = response.json()

    for festival in festivals["items"]:
        if festival["name"] == festival_name:
            return festival


def create_festival(festival, url, header):
    data = {"name": festival, "description": ""}
    header.update({"accept": "application/json"})

    data_str = json.dumps(data, ensure_ascii=False)

    files = {"festival": (None, data_str)}
    response = requests.post(url + "/v1/festivals", headers=header, files=files)
    return response.json()


def assignee_festival(artwork_id, festival_id, url, header):
    data = {"artwork_id": artwork_id, "festival_id": festival_id}
    response = requests.post(
        url + "/v1/festivals/assignee", headers=header, params=data
    )
    return response


def download_image(image_urls: List[HttpUrl]):
    paths = []
    for ind, url in enumerate(image_urls):
        img_data = requests.get(url).content
        with open(f"{ind}.jpg", "wb") as handler:
            handler.write(img_data)
        paths.append(f"{ind}.jpg")
    return paths


async def send_data_to_host(url: str, artworks: List[ArtworkData]):
    token = await create_auth_token(url, auth_data)
    data_schema = {"Authorization": f"Bearer {token}"}

    for artwork in artworks:
        new_artwork = await create_artwork(
            artwork, url, data_schema, artwork.image_urls
        )
        artwork_id = new_artwork["id"]
        artist_current = get_current_artist(artwork.artist_name, url, data_schema)
        if not artist_current:
            artist_current = create_artist(artwork.artist_name, url, data_schema)

        assignee_artist(artwork_id, artist_current["id"], url, data_schema)

        festival_current = get_current_festival(artwork.festival, url, data_schema)

        if not festival_current:
            festival_current = create_festival(artwork.festival, url, data_schema)
        assignee_festival(artwork_id, festival_current["id"], url, data_schema)


data = read_data_from_table("Работы - STENOGRAFFIA.csv")

asyncio.run(send_data_to_host("http://localhost:8000", data))
