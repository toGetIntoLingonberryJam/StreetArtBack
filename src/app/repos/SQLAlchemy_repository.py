from pydantic import BaseModel as BaseSchema

from sqlalchemy import insert, select, update, delete
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import RelationshipProperty, InstrumentedAttribute

from app.db import async_session_maker, Base as ModelBase


class SQLAlchemyRepository:
    model: ModelBase = None
    session: AsyncSession

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, obj_data: BaseSchema | dict) -> ModelBase:
        obj_data = obj_data if isinstance(obj_data, dict) else obj_data.model_dump()

        stmt = insert(self.model).values(**obj_data).returning(self.model)
        res = await self.session.execute(stmt)
        return res.scalar_one()

        # new_obj = self.model(**obj_data)
        # self.session.add(new_obj)
        # await self.session.flush()
        # await self.session.refresh(new_obj)
        # return new_obj

    async def get_all(
        self, offset: int = 0, limit: int | None = None, **filter_by
    ) -> ModelBase:
        stmt = select(self.model).offset(offset=offset)
        if filter_by:
            # TODO: как-то бы вынести и переработать
            # Проверяем, что переданные атрибуты существуют в модели и стоим фильтр используя только существующие
            valid_attributes = {
                attr: getattr(self.model, attr)
                for attr in filter_by.keys()
                if hasattr(self.model, attr)
            }
            filters = {
                attr: value
                for attr, value in filter_by.items()
                if attr in valid_attributes
            }

            # Фильтрация через связь, если атрибут - связанное поле
            for attr, value in filters.items():
                if isinstance(valid_attributes[attr], InstrumentedAttribute):
                    if isinstance(
                        valid_attributes[attr].property, RelationshipProperty
                    ):
                        related_model = valid_attributes[attr].mapper.class_
                        stmt = stmt.join(related_model)
                        for rm_attr, rm_value in value.items():
                            if isinstance(rm_attr, InstrumentedAttribute):
                                rm_attr = rm_attr.name

                            stmt = stmt.filter(
                                valid_attributes[attr].has(**{rm_attr: rm_value})
                            )
                else:
                    stmt = stmt.filter_by(**{attr: value})

        if limit:
            stmt = stmt.limit(limit=limit)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get(self, obj_id: int, **filter_by) -> ModelBase:
        stmt = select(self.model).filter_by(id=obj_id, **filter_by)
        result = await self.session.execute(stmt)
        return result.scalar_one()
        # return await self.session.execute(
        #     self.model.__table__.
        #     select().
        #     where(self.model.id == obj_id)
        # ).scalar_one()

    async def filter(self, **filter_by):
        # # Проверяем, что переданные атрибуты существуют в модели
        # valid_attributes = [attr for attr in kwargs.keys() if hasattr(self.model, attr)]
        # # Строим фильтр, используя только существующие атрибуты
        # filters = [getattr(self.model, attr) == value for attr, value in kwargs.items() if attr in valid_attributes]
        stmt = select(self.model).filter_by(**filter_by)
        # result = await self.session.execute(
        #     self.model.__table__.
        #     select().
        #     filter_by(**filter_by)
        # )
        result = await self.session.execute(stmt)

        return result.scalars().all()

    async def edit(self, obj_id: int, obj_data: BaseSchema | dict) -> int:
        obj_data = obj_data if isinstance(obj_data, dict) else obj_data.model_dump()

        stmt = (
            update(self.model)
            .values(**obj_data)
            .filter_by(id=obj_id)
            .returning(self.model)
        )
        res = await self.session.execute(stmt)
        return res.scalar_one()

    async def delete(self, obj_id: int):
        stmt = delete(self.model).filter_by(id=obj_id)
        res = await self.session.execute(stmt)

        # if res.rowcount == 0:
        #     raise NoResultFound(f"Object with ID {obj_id} not found")

    #
    # async def get(self, obj_id: int) -> ModelBase:
    #     try:
    #         document = await self.session.get(self.model, obj_id)
    #         # await self.session.refresh(new_document)
    #         return document
    #     except Exception:
    #         await self.session.rollback()
    #         raise

    # async def create(self, data: BaseSchema | dict):  # ToDo: Чекни работоспособность
    #     # try:
    #         # data = data if isinstance(data, dict) else data.dict()
    #     new_document = self.model(**data)
    #     self.session.add(new_document)
    #         # self.session.commit()
    #     # except Exception:
    #     #     self.session.rollback()
    #     #     raise
    #
    #     # Обновляем объект, чтобы получить автоматически сгенерированные значения, если таковые есть
    #     await self.session.refresh(new_document)
    #
    #     return new_document

    # async def add_one(self, data: dict) -> ModelBase:
    #     stmt = insert(self.model).values(**data).returning(self.model)
    #     res = await self.session.execute(stmt)
    #     return res.scalar_one()
    #
    # async def edit_one(self, id: int, data: dict) -> int:
    #     stmt = update(self.model).values(**data).filter_by(id=id).returning(self.model.id)
    #     res = await self.session.execute(stmt)
    #     return res.scalar_one()
    #
    # async def find_all(self, **kwargs):
    #     stmt = select(self.model)
    #     if 'options' in kwargs:
    #         for option in kwargs['options']:
    #             stmt = stmt.options(option)
    #     res = await self.session.execute(stmt)
    #     return [row[0] for row in res.all()]
    #
    # async def find_one(self, **filter_by):
    #     stmt = select(self.model).filter_by(**filter_by)
    #     res = await self.session.execute(stmt)
    #     res = res.scalar()
    #     return res
