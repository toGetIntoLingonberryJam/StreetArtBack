import pytest

from app.modules.users.manager import get_user_manager
from app.modules.users.models import get_user_db
from app.modules.users.schemas import UserCreate
from app.utils.unit_of_work import UnitOfWork
from tests.conftest import async_session_maker


@pytest.fixture
def users():
    users = [
        UserCreate(username="test", email="test1@testmail.com", password="password"),
        UserCreate(username="test2", email="test2@testmail.com", password="password"),
        UserCreate(username="test3", email="test3@testmail.com", password="password"),
    ]
    return users


@pytest.fixture(scope="function")
async def empty_users():
    uow = UnitOfWork()
    async with uow:
        await uow.users.delete_all()
        await uow.commit()


@pytest.fixture(scope="function")
async def create_users(users):
    async with async_session_maker() as session:

        user_manager = [item async for item in get_user_manager()][0]
        user_manager.user_db = [item async for item in get_user_db()][0]
        user_manager.user_db.session = session

        # Добавление пользователей в БД
        for user in users:
            await user_manager.create(user_create=user, safe=True)

        # await session.close()
