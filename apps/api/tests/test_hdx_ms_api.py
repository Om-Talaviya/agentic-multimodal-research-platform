"""
API integration tests for Phase 105: HDX-MS Endpoints.
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
async def test_hdx_ms_api_flow(test_app: AsyncClient):
    # 1. Post simulation
    payload = {
        "protein_name": "PCSK9",
        "uniprot_id": "P07550",
        "state_condition": "LIGAND_BOUND",
        "peptides": [
            {"peptide_sequence": "MGTVSSRRA", "start_res": 1, "end_res": 9, "is_binding_site": False},
            {"peptide_sequence": "APGATNEKLFFL", "start_res": 10, "end_res": 21, "is_binding_site": True}
        ]
    }

    res = await test_app.post("/api/v1/hdx-ms/simulate", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["protein_name"] == "PCSK9"
    assert data["total_peptides"] == 2
    assert len(data["uptake_curves"]) > 0
    assert len(data["protection_maps"]) > 0
    exp_id = data["id"]

    # 2. List experiments
    list_res = await test_app.get("/api/v1/hdx-ms/experiments")
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert len(list_data) >= 1

    # 3. Get detail
    detail_res = await test_app.get(f"/api/v1/hdx-ms/experiments/{exp_id}")
    assert detail_res.status_code == 200
    detail_data = detail_res.json()
    assert detail_data["id"] == exp_id
