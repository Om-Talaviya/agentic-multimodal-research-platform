"""
Integration tests for ADC Design REST API (Phase 59).
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
async def test_adc_api_workflow(async_test_session: AsyncSession):
    async def override_get_db():
        yield async_test_session

    app.dependency_overrides[get_db_session] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Create Campaign
        res = await client.post(
            "/api/v1/adc-design/campaigns",
            json={
                "antibody_name": "Sacituzumab",
                "target_antigen": "TROP2",
                "conjugation_chemistry": "Maleimide-Cysteine",
                "target_dar": 7.6,
            },
        )
        assert res.status_code == 201
        data = res.json()
        camp_id = data["id"]
        assert len(data["constructs"]) >= 5

        # 2. Get Campaign Detail
        get_res = await client.get(f"/api/v1/adc-design/campaigns/{camp_id}")
        assert get_res.status_code == 200
        assert get_res.json()["antibody_name"] == "Sacituzumab"

        # 3. List Campaigns
        list_res = await client.get("/api/v1/adc-design/campaigns")
        assert list_res.status_code == 200
        assert any(c["id"] == camp_id for c in list_res.json())
