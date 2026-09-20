"""
API integration tests for Phase 107: Cryptic Pockets Endpoints.
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
async def test_cryptic_pockets_api_flow(test_app: AsyncClient):
    # 1. Post discover
    payload = {
        "target_protein": "API-KRAS",
        "pdb_id": "7T47",
        "trajectory_frames_sampled": 100,
        "candidate_pockets": [
            {
                "pocket_name": "Switch-II",
                "center_x": 12.0, "center_y": 14.0, "center_z": 16.0,
                "apo_volume_a3": 100.0, "holo_volume_a3": 550.0,
                "hydrophobicity_score": 0.80
            }
        ]
    }

    res = await test_app.post("/api/v1/cryptic-pockets/discover", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["target_protein"] == "API-KRAS"
    assert data["detected_cryptic_pockets"] == 1
    assert len(data["pockets"]) == 1
    assert len(data["coupled_networks"]) > 0
    analysis_id = data["id"]

    # 2. List analyses
    list_res = await test_app.get("/api/v1/cryptic-pockets/analyses")
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert len(list_data) >= 1

    # 3. Get detail
    detail_res = await test_app.get(f"/api/v1/cryptic-pockets/analyses/{analysis_id}")
    assert detail_res.status_code == 200
    detail_data = detail_res.json()
    assert detail_data["id"] == analysis_id
