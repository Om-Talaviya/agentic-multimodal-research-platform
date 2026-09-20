"""
API integration tests for Phase 106: Spatial Lipidomics Endpoints.
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
async def test_spatial_lipidomics_api_flow(test_app: AsyncClient):
    # 1. Post process
    payload = {
        "sample_name": "API-Brain-Lipidomics",
        "tissue_type": "Coronal Brain Slice",
        "matrix_type": "DHB",
        "grid_dim": 4,
        "custom_mz_list": [760.585, 788.616]
    }

    res = await test_app.post("/api/v1/spatial-lipidomics/process", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["sample_name"] == "API-Brain-Lipidomics"
    assert data["total_spots"] == 16  # 4x4
    assert len(data["lipid_species"]) == 2
    assert len(data["spatial_spots"]) == 32  # 2 lipids * 16 spots
    ds_id = data["id"]

    # 2. List datasets
    list_res = await test_app.get("/api/v1/spatial-lipidomics/datasets")
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert len(list_data) >= 1

    # 3. Get detail
    detail_res = await test_app.get(f"/api/v1/spatial-lipidomics/datasets/{ds_id}")
    assert detail_res.status_code == 200
    detail_data = detail_res.json()
    assert detail_data["id"] == ds_id
