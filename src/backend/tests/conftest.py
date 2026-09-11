import os

# Settings are read at import time, so these must be set before anything
# under `backend.*` is imported. A real Postgres is required — the models
# use `sqlalchemy.dialects.postgresql.UUID`, which SQLite can't run.
os.environ.setdefault(
    "DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5433/test"
)
os.environ.setdefault("SECRET_KEY", "pytest-only-secret-key-not-for-real-use-32ch")
os.environ.setdefault("CORS_ORIGINS", '["http://localhost:3000"]')

import asyncio

import pytest
import pytest_asyncio
from backend.db.session import get_db
from backend.main import app
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


@pytest.fixture(scope="session")
def event_loop():
    # Session-scoped so it matches the session-scoped `engine` fixture below —
    # pytest-asyncio's default per-function loop would otherwise leave the
    # engine bound to a loop that later tests aren't running on.
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def engine():
    # create_async_engine is lazy — it doesn't actually connect until first
    # used, so declaring this fixture here costs unit tests nothing; only
    # tests/integration/conftest.py's autouse fixture forces a connection.
    eng = create_async_engine(os.environ["DATABASE_URL"], echo=False)
    yield eng
    await eng.dispose()


@pytest_asyncio.fixture
async def session_factory(engine):
    return async_sessionmaker(bind=engine, expire_on_commit=False)


@pytest_asyncio.fixture
async def db_session(session_factory):
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def client(session_factory):
    async def _get_db_override():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = _get_db_override
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
