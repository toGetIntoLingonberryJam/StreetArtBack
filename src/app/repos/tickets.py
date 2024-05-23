from typing import Optional, Type, TypeVar

from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.utils.libs.fastapi_filter.contrib.sqlalchemy import Filter
from app.modules.models import User
from app.modules.tickets.models import TicketArtwork, TicketBase
from app.modules.tickets.utils.classes import TicketModel, TicketRegistry, TicketType
from app.modules.tickets.utils.types import TicketCreateSchemaType
from app.repos.SQLAlchemy_repository import SQLAlchemyRepository


class TicketBaseRepository(SQLAlchemyRepository):
    model = TicketBase  # В момент вызова функций связанных с записью данных в БД это поле переопределяется
    # на требуемое значение, после чего там же и переопределяются на базовый
    # ToDo: подумать как улучшить

    @staticmethod
    async def _validate_and_get_ticket_model_class(
        ticket_model: TicketModel,
    ) -> Type[TicketBase]:
        ticket_model_value_class = TicketRegistry.ticket_classes.get(ticket_model)

        if not issubclass(ticket_model_value_class, TicketBase):
            raise ValueError("Invalid ticket class")

        return ticket_model_value_class

    async def _create_ticket_filter(
        self,
        ticket_model: TicketModel | None,
        ticket_id: int | None = None,
        user_id: int | None = None,
        **filtering_fields,
    ) -> Filter:
        """Создаём фильтрацию по полученной модели и значению дискриминатора"""
        filters = Filter()
        if ticket_model:
            filters.add_filtering_fields(discriminator=ticket_model.value)
        else:
            ticket_model = TicketModel.TICKET

        filters.Constants.model = await self._validate_and_get_ticket_model_class(
            ticket_model=ticket_model
        )

        if ticket_id:
            filters.add_filtering_fields(id=ticket_id)

        if user_id:
            filters.add_filtering_fields(user_id=user_id)

        if filtering_fields:
            filters.add_filtering_fields(**filtering_fields)

        return filters

    async def get_ticket(
        self,
        ticket_id: int,
        ticket_model: TicketModel | None,
        user_id: int | None = None,
    ):
        # ticket_model_value_class = await self._validate_and_get_ticket_model_class(
        #     ticket_model=ticket_model
        # )
        filters = await self._create_ticket_filter(
            ticket_model=ticket_model,
            user_id=user_id,
            ticket_id=ticket_id,
        )

        res = await self.filter(filters=filters)
        if not res:
            raise NoResultFound
        return res[0]

    async def get_all_tickets(
        self,
        ticket_model: TicketModel | None,
        offset: int = 0,
        limit: int | None = None,
        user_id: int | None = None,
    ):
        filters = await self._create_ticket_filter(
            ticket_model=ticket_model, user_id=user_id
        )
        return await self.filter(offset=offset, limit=limit, filters=filters)

    # async def create_ticket(
    #     self,
    #     user: User,
    #     ticket_model: TicketModel,
    #     ticket_type: TicketType,
    #     ticket_schema: TicketCreateSchemaType,
    # ):
    #     ticket_model_value_class = await self._validate_and_get_ticket_model_class(
    #         ticket_model=ticket_model
    #     )
    #     # Динамическое создание класса на основе полученного значения
    #     # self.model = type('DynamicTicket', (ticket_model_value_class,), {})
    #
    #     self.model = ticket_model_value_class
    #
    #     await self.create(ticket_data)
    #
    #     # Да-да, тот самый костыль xD
    #     self.model = TicketBase


class TicketArtworkRepository(TicketBaseRepository):
    model = TicketArtwork
