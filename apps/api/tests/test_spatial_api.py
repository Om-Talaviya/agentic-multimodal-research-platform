"""Integration tests for Spatial Transcriptomics REST API (Phase 42)."""
import uuid
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from database.connection import Base
from database.models.user import User as DBUser
from api.dependencies import get_current_user, get_db_session
from main import app

@pytest.fixture
async def async_test_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        yield session
    
    await engine.dispose()

@pytest.fixture
def mock_user():
    return DBUser(
        id=uuid.uuid4(),
        username="spatial_lead",
        email="spatial_lead@broadinstitute.org",
        password_hash="mocked",
        role="Researcher",
    )

@pytest.mark.asyncio
async def test_spatial_api_lifecycle(async_test_session: AsyncSession, mock_user: DBUser):
    async def override_get_db():
        yield async_test_session

    async def override_get_user():
        return mock_user

    app.dependency_overrides[get_db_session] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_user

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. POST /api/v1/spatial/analyze
        req_payload = {
            "title": "Hepatocellular Carcinoma Visium Sample",
            "tissue_type": "Liver HCC",
            "technology": "10x Visium",
            "n_spots": 100,
            "description": "Spatial slide analysis of HCC tumor-stroma boundary"
        }
        res = await client.post("/api/v1/spatial/analyze", json=req_payload)
        assert res.status_code == 201
        data = res.json()
        dataset_id = data["id"]
        assert data["title"] == "Hepatocellular Carcinoma Visium Sample"
        assert data["total_spots"] == 100

        # 2. GET /api/v1/spatial/datasets
        res_list = await client.get("/api/v1/spatial/datasets")
        assert res_list.status_code == 200
        assert len(res_list.json()) >= 1

        # 3. GET /api/v1/spatial/datasets/{id}
        res_get = await client.get(f"/api/v1/spatial/datasets/{dataset_id}")
        assert res_get.status_code == 200
        assert res_get.json()["id"] == dataset_id

        # 4. GET /api/v1/spatial/datasets/{id}/spots
        res_spots = await client.get(f"/api/v1/spatial/datasets/{dataset_id}/spots")
        assert res_spots.status_code == 200
        assert len(res_spots.json()) == 100

        # 5. GET /api/v1/spatial/datasets/{id}/domains
        res_domains = await client.get(f"/api/v1/spatial/datasets/{dataset_id}/domains")
        assert res_domains.status_code == 200
        assert len(res_domains.json()) >= 3

        # 6. GET /api/v1/spatial/datasets/{id}/communications
        res_comms = await client.get(f"/api/v1/spatial/datasets/{dataset_id}/communications")
        assert res_comms.status_code == 200
        assert len(res_comms.json()) >= 4

        # 7. DELETE /api/v1/spatial/datasets/{id}
        res_del = await client.delete(f"/api/v1/spatial/datasets/{dataset_id}")
        assert res_del.status_code == 204

    app.dependency_overrides.clear()
