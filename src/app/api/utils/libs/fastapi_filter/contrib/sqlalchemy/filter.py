# -*- coding: utf-8 -*-
import itertools
from enum import Enum
from typing import Union

from pydantic import ValidationInfo, field_validator
from sqlalchemy import or_
from sqlalchemy.orm import Query, class_mapper, joinedload
from sqlalchemy.sql.selectable import Select

from ...base.filter import BaseFilterModel


def _backward_compatible_value_for_like_and_ilike(value: str):
    """Add % if not in value to be backward compatible.

    Args:
        value (str): The value to filter.

    Returns:
        Either the unmodified value if a percent sign is present, the value wrapped in % otherwise to preserve
        current behavior.
    """
    if "%" not in value:
        value = f"%{value}%"
    return value


_orm_operator_transformer = {
    "eq": lambda value: ("__eq__", value),
    "neq": lambda value: ("__ne__", value),
    "gt": lambda value: ("__gt__", value),
    "gte": lambda value: ("__ge__", value),
    "in": lambda value: ("in_", value),
    "isnull": lambda value: ("is_", None) if value is True else ("is_not", None),
    "lt": lambda value: ("__lt__", value),
    "lte": lambda value: ("__le__", value),
    "like": lambda value: (
        "like",
        _backward_compatible_value_for_like_and_ilike(value),
    ),
    "ilike": lambda value: (
        "ilike",
        _backward_compatible_value_for_like_and_ilike(value),
    ),
    # XXX(arthurio): Mysql excludes None values when using `in` or `not in` filters.
    "not": lambda value: ("is_not", value),
    "not_in": lambda value: ("not_in", value),
}
"""Operators à la Django.

Examples:
    my_datetime__gte
    count__lt
    name__isnull
    user_id__in
"""


class Filter(BaseFilterModel):
    """Base filter for orm related filters.

    All children must set:
        ```python
        class Constants(Filter.Constants):
            model = MyModel
        ```

    It can handle regular field names and Django style operators.

    Example:
        ```python
        class MyModel:
            id: PrimaryKey()
            name: StringField(nullable=True)
            count: IntegerField()
            created_at: DatetimeField()

        class MyModelFilter(Filter):
            id: Optional[int]
            id__in: Optional[str]
            count: Optional[int]
            count__lte: Optional[int]
            created_at__gt: Optional[datetime]
            name__isnull: Optional[bool]
    """

    class Direction(str, Enum):
        asc = "asc"
        desc = "desc"

    @field_validator("*", mode="before")
    def split_str(cls, value, field: ValidationInfo):
        if (
            field.field_name == cls.Constants.ordering_field_name
            or field.field_name.endswith("__in")
            or field.field_name.endswith("__not_in")
        ):
            # and isinstance(value, str):
            # if not value:
            #     # Empty string should return [] not ['']
            #     return []
            # return list(value.split(","))

            if isinstance(value, str):
                value = map(str.strip, value.split(","))
            elif isinstance(value, list) and all(isinstance(x, str) for x in value):
                value = map(
                    str.strip,
                    itertools.chain.from_iterable(x.split(",") for x in value),
                )

        return value

    def filter(self, query: Union[Query, Select]):
        for field_name, value in self.filtering_fields:
            field_value = getattr(self, field_name)
            base_model = self.Constants.model
            if isinstance(field_value, Filter):
                if "__" in field_name:
                    related_field, operator = field_name.split("__")
                    base_model = self.Constants.model
                    query = query.join(getattr(base_model, related_field))
                query = field_value.filter(query)
            else:
                if "__" in field_name:
                    is_has_operator = _orm_operator_transformer.get(
                        field_name.rsplit("__", 1)[1]
                    )
                    if is_has_operator:
                        field_name, operator = field_name.rsplit("__", 1)
                        operator, value = _orm_operator_transformer[operator](value)
                    else:
                        operator = "__eq__"

                    base_model = self.Constants.model
                    while "__" in field_name:
                        related_field_name, field_name = field_name.split("__", 1)

                        # Проверяем, является ли отношение "многие ко многим"
                        relationship_ = getattr(base_model, related_field_name)
                        if relationship_.property.uselist is not None:
                            # Используем join для связи с промежуточной таблицей
                            query = query.join(relationship_)
                        else:
                            # Обычный join для отношений "один ко многим"
                            query = query.join(getattr(base_model, related_field_name))
                        base_model = getattr(
                            base_model, related_field_name
                        ).property.mapper.class_
                else:
                    operator = "__eq__"

                if (
                    self.Constants.search_model_fields
                    and field_name == self.Constants.search_field_name
                ):
                    res_filter = list()

                    for field in self.Constants.search_model_fields:
                        if "__" in field:
                            related_fields = field.split("__")
                            related_field_name = related_fields.pop()
                            base_model = self.Constants.model
                            for related_field in related_fields:
                                query = query.outerjoin(
                                    getattr(base_model, related_field)
                                )

                                base_model = getattr(
                                    base_model, related_field
                                ).property.mapper.class_

                            search_field = getattr(base_model, related_field_name)
                        else:
                            search_field = getattr(self.Constants.model, field)

                        res_filter.append(search_field.ilike("%" + value + "%"))

                    query = query.filter(or_(*res_filter))
                else:
                    # model_field = getattr(self.Constants.model, field_name)
                    model_field = getattr(base_model, field_name)

                    query = query.filter(getattr(model_field, operator)(value))

        return query

    def sort(self, query: Union[Query, Select]):
        if not self.ordering_values:
            return query

        for field_name in self.ordering_values:
            direction = Filter.Direction.asc
            if field_name.startswith("-"):
                direction = Filter.Direction.desc
            field_name = field_name.replace("-", "").replace("+", "")

            base_model = self.Constants.model
            while "__" in field_name:
                related_filed_name, field_name = field_name.split("__", 1)
                query = query.join(getattr(base_model, related_filed_name))
                base_model = getattr(
                    base_model, related_filed_name
                ).property.mapper.class_

            order_by_field = getattr(base_model, field_name)

            query = query.order_by(getattr(order_by_field, direction)())

        return query
