import os
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
import asyncio

from app.database import Base, get_db
from app.main import app

TEST_DB_URL = 'sqlite+aiosqlite:///./test_db.sqlite3'


@pytest.fixture(scope='session', autouse=True)
def setup_test_db():
    """Создаёт тестовую БД один раз на всю сессию."""

    engine = create_async_engine(TEST_DB_URL)

    async def _create():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    loop = asyncio.new_event_loop()
    loop.run_until_complete(_create())
    loop.close()

    yield

    if os.path.exists('./test_db.sqlite3'):
        os.remove('./test_db.sqlite3')


@pytest.fixture
async def db():
    """Сессия БД для тестов."""

    engine = create_async_engine(TEST_DB_URL)
    test_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with test_session() as session:
        yield session


@pytest.fixture
async def client(db):
    """Асинхронный клиент для тестирования API."""

    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        yield ac

    app.dependency_overrides.clear()
