import pytest

from app.utils.unit_of_work import UnitOfWork


@pytest.mark.usefixtures("clear_database", "create_users", "create_tickets")
class TestTickets:
    async def test_count_tickets(self):
        uow = UnitOfWork()
        async with uow:
            assert await uow.tickets.count() == 3  # len(tickets) = 3
