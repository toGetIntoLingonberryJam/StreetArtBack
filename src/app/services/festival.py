from typing import Optional

from fastapi import UploadFile

from app.api.utils.libs.fastapi_filter.contrib.sqlalchemy import Filter
from fastapi_pagination import Params
from sqlalchemy import exc
from sqlalchemy.exc import NoResultFound

from app.modules.cloud_storage.schemas.image import ImageCreateSchema
from app.modules.festivals.schemas import FestivalCreateSchema
from app.services.cloud_storage import CloudStorageService
from app.utils.exceptions import ObjectNotFoundException
from app.utils.unit_of_work import UnitOfWork


class FestivalService:
    async def get_festival_by_id(self, uow: UnitOfWork, festival_id: int):
        try:
            async with uow:
                festival = await uow.festival.get(festival_id)
                return festival
        except exc.NoResultFound:
            raise ObjectNotFoundException("Festival not found")

    async def create_festival(
        self,
        uow: UnitOfWork,
        festival_schema: FestivalCreateSchema,
        image: Optional[UploadFile] = None,
    ):
        async with uow:
            festival_dict = festival_schema.model_dump()
            if image:
                cloud_file = await CloudStorageService.upload_to_yandex_disk(
                    image=image
                )
                image_schema = ImageCreateSchema(
                    image_url=cloud_file.public_url,
                    public_key=cloud_file.public_key,
                    file_path=cloud_file.file_path,
                )
                image_model = await uow.images.create(image_schema)
                festival_dict["image"] = image_model
                festival_dict["image_id"] = image_model.id
            festival = await uow.festival.create(festival_dict)
            await uow.commit()
            await uow.session.refresh(festival)
            return festival

    async def get_all_festival(
        self,
        uow: UnitOfWork,
        pagination: Params | None = None,
        filters: Filter | None = None,
        **filter_by
    ):
        async with uow:
            offset: int = 0
            limit: int | None = None

            if pagination:
                pagination_raw_params = pagination.to_raw_params()
                offset = pagination_raw_params.offset
                limit = pagination_raw_params.limit

            festivals = await uow.festival.filter(
                offset=offset, limit=limit, filters=filters, filter_by=filter_by
            )
            return festivals

    async def delete_festival(self, uow: UnitOfWork, festival_id: int):
        async with uow:
            await uow.festival.delete(festival_id)

    async def update_artwork_festival(
        self, uow: UnitOfWork, artwork_id: int, festival_id: int
    ):
        async with uow:
            try:
                festival = await uow.festival.get(festival_id)
            except NoResultFound:
                raise ObjectNotFoundException("Фестиваль не найден.")

            try:
                artwork = await uow.artworks.get(artwork_id)
                artwork.festival = festival
                await uow.commit()
                return artwork
            except NoResultFound:
                raise ObjectNotFoundException("Арт-объект не найден.")
