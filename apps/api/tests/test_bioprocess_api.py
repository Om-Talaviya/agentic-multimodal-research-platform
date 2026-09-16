"""
Integration tests for Bioprocess Digital Twin REST API (Phase 62).
"""
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from api.dependencies import get_db_session
from database.connection import Base
from main import app


@pytest.fixture
async def async_test_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_factory = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session_factory() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_bioprocess_api_workflow(async_test_session: AsyncSession):
    async def override_get_db():
        yield async_test_session

    app.dependency_overrides[get_db_session] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Create Run
        res = await client.post(
            "/api/v1/bioprocess/runs",
            json={
                "run_name": "Bioreactor-Test-API",
                "cell_line": "CHO-K1",
                "bioreactor_type": "Fed-Batch Stirred Tank",
                "working_volume_liters": 50.0,
            },
        )
        assert res.status_code == 201
        data = res.json()
        run_id = data["id"]
        assert len(data["telemetry_points"]) == 15

        # 2. Get Run Detail
        get_res = await client.get(f"/api/v1/bioprocess/runs/{run_id}")
        assert get_res.status_code == 200
        assert get_res.json()["run_name"] == "Bioreactor-Test-API"

        # 3. List Runs
        list_res = await client.get("/api/v1/bioprocess/runs")
        assert list_res.status_code == 200
        assert any(r["id"] == run_id for r in list_res.json())
