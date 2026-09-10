import pytest_asyncio

from backend.db.base import Base
import backend.models  # noqa: F401 — registers every model on Base.metadata


@pytest_asyncio.fixture(autouse=True)
async def _clean_schema(engine):
    """
    Fresh schema per test — simplest correct isolation for a suite this
    size. Scoped to tests/integration/ only (not the root conftest) so
    unit tests never need a reachable Postgres at all.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
