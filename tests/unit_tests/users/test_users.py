import pytest
from app.utils.unit_of_work import UnitOfWork


@pytest.mark.usefixtures("clear_database", "create_users")
class TestUsers:
    async def test_count_users(self):
        uow = UnitOfWork()
        async with uow:
            assert await uow.users.count() == 3  # len(users) = 3
