from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

engine = create_async_engine(
    settings.db_url_async,
    echo=False,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

sync_engine = create_engine(settings.db_url)
sync_session = sessionmaker(bind=sync_engine)

class Base(DeclarativeBase):
    """Базовый класс для всех моделей."""

    pass


async def get_db():
    """
    Асинхронная зависимость FastAPI.
    Возвращает сессию БД и закрывает после использования.
    """

    async with AsyncSessionLocal() as db:
        yield db
