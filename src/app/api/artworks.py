from fastapi import APIRouter

from app.modules.artworks.schemas.artwork_location import ArtworkLocation
from app.utils.dependencies import UOWDep
from app.modules.artworks.schemas.artwork import ArtworkCreate, Artwork, ArtworkEdit
from app.services.artworks import ArtworksService

router_artworks = APIRouter(prefix="/artwork", tags=["artwork"])


@router_artworks.post("/create/", response_model=Artwork)
async def create_artwork(artwork_data: ArtworkCreate, uow: UOWDep):

    artwork = await ArtworksService().create_artwork(uow, artwork_data)

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


@router_artworks.get('/show/locations/', response_model=list[ArtworkLocation])
async def show_artwork_locations(uow: UOWDep):
    # Возвращает локации арт-объектов, если местоположение не указано - выведено не будет.
    locations = await ArtworksService().get_artworks_locations(uow)
    return locations




