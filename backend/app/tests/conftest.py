import asyncio
import uuid
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.core.database import get_db
from app.main import app
from app.models.base import Base

# Use a separate test database
TEST_DATABASE_URL = settings.DATABASE_URL.replace("/finpulse", "/finpulse_test")
TEST_DATABASE_URL_SYNC = TEST_DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

# Align sync sessions (fulfillment webhooks/tasks) with the async test database
settings.DATABASE_URL_SYNC = TEST_DATABASE_URL_SYNC
from app.core import sync_database

sync_database.sync_engine = create_engine(TEST_DATABASE_URL_SYNC, pool_pre_ping=True)
sync_database.SyncSessionLocal = sessionmaker(bind=sync_database.sync_engine, autocommit=False, autoflush=False)

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        try:
            yield db_session
            await db_session.commit()
        except Exception:
            await db_session.rollback()
            raise

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
