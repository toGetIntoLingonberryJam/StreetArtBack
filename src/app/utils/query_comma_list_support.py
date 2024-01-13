import itertools
import types
import weakref
from typing import Any

from pydantic import GetCoreSchemaHandler, TypeAdapter
from pydantic_core import CoreSchema, core_schema


class TypeParametersMemoizer(type):
    _generics_cache = weakref.WeakValueDictionary()

    def __getitem__(cls, typeparams):
        # prevent duplication of generic types
        if typeparams in cls._generics_cache:
            return cls._generics_cache[typeparams]

        # middleware class for holding type parameters
        class TypeParamsWrapper(cls):
            __type_parameters__ = (
                typeparams if isinstance(typeparams, tuple) else (typeparams,)
            )
            __type_adapter__ = TypeAdapter(list[__type_parameters__])

            @classmethod
            def _get_type_parameters(cls):
                return cls.__type_parameters__

            @classmethod
            def _get_type_adapter(cls):
                return cls.__type_adapter__

        wrapper = cls._generics_cache[typeparams] = types.GenericAlias(
            TypeParamsWrapper, typeparams
        )
        return wrapper


class CommaSeparatedList(list, metaclass=TypeParametersMemoizer):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_before_validator_function(
            cls.validate, handler(list[cls._get_type_parameters()])
        )

    @classmethod
    def validate(cls, v: Any):
        adapter = cls._get_type_adapter()
        if isinstance(v, str):
            v = map(str.strip, v.split(","))
        elif isinstance(v, list) and all(isinstance(x, str) for x in v):
            v = map(str.strip, itertools.chain.from_iterable(x.split(",") for x in v))
        return adapter.validate_python(v)

    @classmethod
    def _get_type_parameters(cls):
        raise NotImplementedError("should be overridden in metaclass")

    @classmethod
    def _get_type_adapter(cls) -> TypeAdapter:
        raise NotImplementedError("should be overridden in metaclass")
