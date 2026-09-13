"""Tests for database session dependency injection in FastAPI."""

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from database.connection import Base, get_db_session, get_session
from main import app


@pytest.mark.asyncio
async def test_get_db_session_yields_real_async_session():
    """Verify get_db_session yields an actual AsyncSession instance."""
    session_gen = get_db_session()
    session = await session_gen.__anext__()
    try:
        assert isinstance(session, AsyncSession)
    finally:
        try:
            await session_gen.__anext__()
        except StopAsyncIteration:
            pass


@pytest.mark.asyncio
async def test_get_session_context_manager_compatibility():
    """Verify get_session still works as an async context manager."""
    async with get_session() as session:
        assert isinstance(session, AsyncSession)


@pytest.mark.asyncio
async def test_live_health_check_with_real_session_executes_db():
    """Test GET /api/v1/health with real SQLite in-memory database without mocking get_db_session."""
    from database import connection as db_conn

    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    test_session_maker = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

    # Save original session maker and engine
    orig_engine = db_conn.engine
    orig_maker = db_conn.async_session_maker

    db_conn.engine = test_engine
    db_conn.async_session_maker = test_session_maker

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()
        assert "checks" in data
        assert data["checks"]["database"] == "healthy"
    finally:
        db_conn.engine = orig_engine
        db_conn.async_session_maker = orig_maker
        await test_engine.dispose()
