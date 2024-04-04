import pytest

from app.modules.tickets.schemas.ticket_base import TicketCreateSchema
from app.modules.tickets.utils.classes import TicketType
from app.services.tickets import TicketsService
from app.utils.unit_of_work import UnitOfWork


@pytest.fixture
def tickets():
    tickets = [
        TicketCreateSchema(
            ticket_type=TicketType.CREATE,
            reason="Добавление Арт-Объекта на улице Калинина",
        ),
        TicketCreateSchema(
            ticket_type=TicketType.CREATE,
            reason="Добавление Арт-Объекта на улице Пушкина",
        ),
        TicketCreateSchema(
            ticket_type=TicketType.CREATE,
            reason="Добавление Арт-Объекта на улице Татищева",
        ),
    ]
    return tickets


@pytest.fixture(scope="function")
async def empty_tickets():
    uow = UnitOfWork()
    async with uow:
        await uow.tickets.delete_all()
        await uow.commit()


@pytest.fixture(scope="function")
async def create_tickets(tickets):
    uow = UnitOfWork()
    async with uow:
        first_user_in_table = (await uow.users.get_all(offset=0, limit=1))[0]
        for ticket in tickets:
            await TicketsService.create_ticket(
                uow=uow, ticket_schema=ticket, user=first_user_in_table
            )

        await uow.commit()
