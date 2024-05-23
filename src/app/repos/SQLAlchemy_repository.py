from typing import Any, Sequence, Type, TypeVar

from pydantic import BaseModel as BaseSchema
from sqlalchemy import Select, delete, func, inspect, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import (
    DeclarativeBase,
    InstrumentedAttribute,
    RelationshipProperty,
    with_polymorphic,
)

from app.api.utils.libs.fastapi_filter.contrib.sqlalchemy import Filter
from app.db import Base

# T = TypeVar("T", bound=Base)


class SQLAlchemyRepository:
    model: Type[DeclarativeBase]
    session: AsyncSession

    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    async def _select(model) -> Select[Any]:
        mapper = inspect(model)
        if mapper.polymorphic_on is not None:
            # Модель является родительской, получить все дочерние классы
            stmt = select(with_polymorphic(model, "*"))
        else:
            stmt = select(model)

        return stmt

    async def _filter(
        self, stmt: Select, filters: Filter | None = None, **filter_by
    ) -> Select[Any]:
        if filters:
            if hasattr(filters, "ordering_values"):
                stmt = filters.sort(stmt)
            if hasattr(filters, "filtering_fields"):
                stmt = filters.filter(stmt)

        if filter_by:
            # TODO: Проработать тот вариант, что может быть передано вложенное связное поле (artwork__artist__username)
            # Проверяем, что переданные атрибуты существуют в модели и стоим фильтр используя только существующие
            valid_attributes = {
                attr: getattr(self.model, attr)
                for attr in filter_by.keys()
                if hasattr(self.model, attr)
            }
            filters_by = {
                attr: value
                for attr, value in filter_by.items()
                if attr in valid_attributes
            }

            # Фильтрация через связь, если атрибут - связанное поле
            for attr, value in filters_by.items():
                if isinstance(
                    valid_attributes[attr], InstrumentedAttribute
                ) and isinstance(valid_attributes[attr].property, RelationshipProperty):
                    related_model = valid_attributes[attr].mapper.class_
                    stmt = stmt.join(related_model)
                    for rm_attr, rm_value in value.items():
                        if isinstance(rm_attr, InstrumentedAttribute):
                            rm_attr = rm_attr.name

                        stmt = stmt.filter(
                            valid_attributes[attr].any(**{rm_attr: rm_value})
                        )

                        # ToDo: костыль жопа
                        stmt = stmt.distinct()
                else:
                    stmt = stmt.filter_by(**{attr: value})

        return stmt

    async def create(self, obj_data: BaseSchema | dict) -> DeclarativeBase:
        obj_data = (
            obj_data if isinstance(obj_data, dict) else obj_data.model_dump()
        )  # ?? exclude_none=True, exclude_unset=True

        # stmt = insert(self.model).values(**obj_data).returning(self.model)
        # res = await self.session.execute(stmt)
        # return res.scalar_one()

        new_obj = self.model(**obj_data)
        self.session.add(new_obj)
        await self.session.flush()
        await self.session.refresh(new_obj)
        return new_obj

    async def create_many(
        self, obj_data_list: list[BaseSchema | dict]
    ) -> list[DeclarativeBase]:
        """Создает несколько объектов в базе данных на основе переданных данных."""
        try:
            # Преобразование данных в объекты модели
            new_objects = [
                self.model(
                    **(obj_data if isinstance(obj_data, dict) else obj_data.model_dump())
                )
                for obj_data in obj_data_list
            ]

            # Добавление всех новых объектов в сессию одним вызовом
            self.session.add_all(new_objects)
            await self.session.flush()

            # # Обновление каждого объекта после flush
            # for obj in new_objects:
            #     await self.session.refresh(obj)

            return new_objects
        except Exception as e:
            # Обработка исключений
            print(f"Ошибка при создании объектов: {e}")
            await self.session.rollback()
            return []

    async def get_all(
        self, offset: int = 0, limit: int | None = None
    ) -> Sequence[Type[DeclarativeBase]]:
        stmt = await self._select(self.model)

        stmt = stmt.offset(offset=offset)

        if limit:
            stmt = stmt.limit(limit=limit)

        result = await self.session.execute(stmt)
        items = result.scalars().all()
        return items

    async def get(
        self, obj_id: int, filters: Filter | None = None, **filter_by
    ) -> Type[DeclarativeBase]:
        """Возвращает объект, или, если не найден - raise NoResultFound"""
        stmt = await self._select(self.model)
        stmt = stmt.filter_by(id=obj_id)
        result = await self.session.execute(stmt)
        # filter_by["id"] = obj_id
        # a = await self._filter(filters=filters, **filter_by)
        return result.unique().scalar_one()

    async def filter(
        self,
        offset: int = 0,
        limit: int | None = None,
        filters: Filter | None = None,
        **filter_by,
    ):
        stmt = await self._select(self.model)

        stmt = stmt.offset(offset=offset)

        if limit:
            stmt = stmt.limit(limit=limit)

        stmt = await self._filter(stmt=stmt, filters=filters, **filter_by)

        result = await self.session.execute(stmt)

        return result.unique().scalars().all()

    async def edit(self, obj_id: int, obj_data: BaseSchema | dict | None):
        obj_data = (
            obj_data
            if isinstance(obj_data, dict)
            else obj_data.model_dump(exclude_none=True, exclude_unset=True)
        )

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

        # return res.scalar_one()

    async def delete_all(self):
        stmt = delete(self.model)

        await self.session.execute(stmt)
        await self.session.commit()

    async def count(self) -> int:
        query = select(func.count(self.model.id)).select_from(self.model)
        items_count = await self.session.execute(query)
        # self.session.commit()
        return items_count.scalar()
