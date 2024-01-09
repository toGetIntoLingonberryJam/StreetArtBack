from typing import Type

from sqlalchemy.exc import NoResultFound

from app.api.utils.libs.fastapi_filter.contrib.sqlalchemy import Filter
from app.modules.tickets.models import TicketBase, ArtworkTicket
from app.modules.tickets.utils.classes import TicketRegistry, TicketModel
from app.repos.SQLAlchemy_repository import SQLAlchemyRepository


class TicketBaseRepository(SQLAlchemyRepository):
    model = TicketBase

    @staticmethod
    async def _validate_and_get_ticket_model_class(
        ticket_model_enum_value: TicketModel,
    ) -> Type[TicketBase]:
        ticket_model_value_class = TicketRegistry.ticket_classes.get(
            ticket_model_enum_value
        )

        if not issubclass(ticket_model_value_class, TicketBase):
            raise ValueError("Invalid ticket class")

        return ticket_model_value_class

    async def _create_ticket_filter(
        self, ticket_model_enum_value: TicketModel, **filtering_fields
    ) -> Filter:
        # Создаём фильтрацию по полученной модели и значению дискриминатора
        filters = Filter()
        filters.Constants.model = await self._validate_and_get_ticket_model_class(
            ticket_model_enum_value=ticket_model_enum_value
        )
        filters.add_filtering_fields(discriminator=ticket_model_enum_value.value)
        if filtering_fields:
            filters.add_filtering_fields(**filtering_fields)

        return filters

    async def get_ticket_by_ticket_model(
        self, ticket_id: int, ticket_model_enum_value: TicketModel
    ):
        ticket_model_value_class = await self._validate_and_get_ticket_model_class(
            ticket_model_enum_value=ticket_model_enum_value
        )
        # TODO: Пересмотри выполнение filter'а, который кастомный. Чет некорректные запросы шлёт
        #  поэтому пришлось сделать через kwargs'ы, а не через собственный фильтр. Предыдущий метод запускается
        #  только для того, чтобы прошла "валидация".
        filters = {"discriminator": ticket_model_enum_value.value, "id": ticket_id}
        res = await self.filter(**filters)
        if not res:
            raise NoResultFound
        return res[0]

    async def get_all_tickets_by_ticket_model(
        self,
        ticket_model_enum_value: TicketModel,
        offset: int = 0,
        limit: int | None = None,
    ):
        filters = await self._create_ticket_filter(ticket_model_enum_value)
        return await self.filter(offset=offset, limit=limit, filters=filters)

    # async def create_ticket_by_ticket_model(
    #         self,
    #         user: User,
    #         ticket_model_enum_value: TicketModel,
    #         ticket_data: TicketCreateSchemaType
    # ):
    #     ticket_model_value_class = await self._validate_and_get_ticket_model_class(
    #         ticket_model_enum_value=ticket_model_enum_value)

    # Я могу получить класс из енума, и, по этому классу надо будет создать новую модель, но сначала репозиторий,
    # т.к. он же отвечает за работу с БД...


class ArtworkTicketRepository(TicketBaseRepository):
    model = ArtworkTicket
