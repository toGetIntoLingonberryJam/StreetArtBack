from typing import Optional

from fastapi import UploadFile
from sqlalchemy.exc import NoResultFound

from app.api.utils.libs.fastapi_filter.contrib.sqlalchemy import Filter
from app.api.utils.paginator import MyParams
from app.modules.artists.schemas.artist import ArtistCreateSchema
from app.modules.images.schemas.image import ImageCreateSchema
from app.services.cloud_storage import CloudStorageService
from app.utils.exceptions import (
    IncorrectInput,
    ObjectNotFoundException,
    UserNotFoundException,
)
from app.utils.unit_of_work import UnitOfWork


class ArtistsService:
    async def get_artist_by_id(self, uow: UnitOfWork, artist_id: int):
        try:
            async with uow:
                artist = await uow.artist.get(artist_id)
                return artist
        except NoResultFound:
            raise ObjectNotFoundException("Artist not found")

    async def create_artist(
            self,
            uow: UnitOfWork,
            artist_schema: ArtistCreateSchema,
            image: Optional[UploadFile] = None,
    ):
        async with uow:
            if artist_schema.user_id:
                try:
                    user = await uow.users.get(artist_schema.user_id)
                    if not user.is_verified:
                        raise IncorrectInput("Пользователь не верифициован.")
                except NoResultFound:
                    raise UserNotFoundException("Пользователь не найден.")

                artist_user = await uow.artist.filter(user_id=user.id)
                if artist_user:
                    raise IncorrectInput("Пользователь уже является художником.")
                user = await uow.users.edit(user.id, {"is_artist": True})
            else:
                artist_schema.user_id = None

            artist_dict = artist_schema.model_dump()
            if image:
                cloud_file = await CloudStorageService.upload_to_yandex_disk(image=image)
                image_schema = ImageCreateSchema(
                    image_url=cloud_file.public_url,
                    public_key=cloud_file.public_key,
                    file_path=cloud_file.file_path,
                    blurhash=cloud_file.blurhash
                )
                image_model = await uow.images.create(image_schema)
                artist_dict["image"] = image_model
                artist_dict["image_id"] = image_model.id
            artist = await uow.artist.create(artist_dict)
            artist.artworks = []
            await uow.commit()
            return artist

    async def get_all_artist(
        self,
        uow: UnitOfWork,
        pagination: MyParams | None = None,
        filters: Filter | None = None,
        **filter_by,
    ):
        async with uow:
            offset: int = 0
            limit: int | None = None

            if pagination:
                pagination_raw_params = pagination.to_raw_params()
                offset = pagination_raw_params.offset
                limit = pagination_raw_params.limit
            artists = await uow.artist.filter(
                offset=offset, limit=limit, filters=filters, filter_by=filter_by
            )
            return artists

    async def delete_artist(self, uow: UnitOfWork, artist_id: int):
        async with uow:
            await uow.artist.delete(artist_id)

    async def get_artist_by_user_id(self, uow: UnitOfWork, user_id: int):
        async with uow:
            artist = await uow.artist.filter(user_id=user_id)
            return artist

    async def update_artwork_artist(self, uow: UnitOfWork, artwork_id: int, artist_id: int):
        async with uow:
            try:
                artist = await uow.artist.get(artist_id)
            except NoResultFound:
                raise ObjectNotFoundException("Художник не найден.")

            try:
                artwork = await uow.artworks.get(artwork_id)
                if artist not in artwork.artist:
                    artwork.artist.append(artist)
                await uow.commit()
                return artwork
            except NoResultFound:
                raise ObjectNotFoundException("Арт-объект не найден.")

    async def remove_artwork_artist(self, uow: UnitOfWork, artwork_id: int, artist_id: int):
        async with uow:
            try:
                artist = await uow.artist.get(artist_id)
            except NoResultFound:
                raise ObjectNotFoundException("Художник не найден.")

            try:
                artwork = await uow.artworks.get(artwork_id)
                if artist in artwork.artist:
                    artwork.artist.remove(artist)
                await uow.commit()
                return artwork
            except NoResultFound:
                raise ObjectNotFoundException("Арт-объект не найден.")
