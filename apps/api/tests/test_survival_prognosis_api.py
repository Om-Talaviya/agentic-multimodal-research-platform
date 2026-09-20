"""
API integration tests for Phase 110: Survival Prognosis Endpoints.
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
async def test_survival_prognosis_api_flow(test_app: AsyncClient):
    payload = {
        "model_name": "API-TCGA-Stratifier",
        "cancer_cohort": "TCGA-LUAD",
        "sample_size": 50
    }

    # 1. Simulate and stratify
    res = await test_app.post("/api/v1/survival-prognosis/stratify", json=payload)
    assert res.status_code == 201, res.text
    data = res.json()
    assert data["status"] == "success"
    assert "model_id" in data
    model_id = data["model_id"]

    # 2. Retrieve model details
    get_res = await test_app.get(f"/api/v1/survival-prognosis/models/{model_id}")
    assert get_res.status_code == 200, get_res.text
    model_data = get_res.json()
    assert model_data["model_name"] == "API-TCGA-Stratifier"
    assert model_data["cancer_cohort"] == "TCGA-LUAD"
    assert len(model_data["curves"]) == 3
