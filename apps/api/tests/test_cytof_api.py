"""
API integration tests for Phase 109: CyTOF Endpoints.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from database.connection import Base
from api.dependencies import get_db
from main import app

@pytest.fixture
async def test_app():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async def override_get_db():
        async with async_session() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.mark.asyncio
async def test_cytof_api_simulation_and_retrieval(test_app: AsyncClient):
    payload = {
        "experiment_name": "API-Test-PBMC-CyTOF",
        "tissue_type": "PBMC",
        "cell_count": 5000,
        "cofactor": 5.0
    }

    # 1. Simulate and persist
    res = await test_app.post("/api/v1/cytof/simulate", json=payload)
    assert res.status_code == 201, res.text
    data = res.json()
    assert data["status"] == "success"
    assert "experiment_id" in data
    exp_id = data["experiment_id"]

    # 2. Retrieve experiment details
    get_res = await test_app.get(f"/api/v1/cytof/experiments/{exp_id}")
    assert get_res.status_code == 200, get_res.text
    exp_data = get_res.json()
    assert exp_data["experiment_name"] == "API-Test-PBMC-CyTOF"
    assert len(exp_data["channels"]) > 0
    assert len(exp_data["clusters"]) > 0
