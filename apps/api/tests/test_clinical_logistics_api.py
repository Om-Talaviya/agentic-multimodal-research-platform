"""
Integration tests for Clinical Trial Logistics REST API (Phase 63).
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
async def test_clinical_logistics_api_workflow(async_test_session: AsyncSession):
    async def override_get_db():
        yield async_test_session

    app.dependency_overrides[get_db_session] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Create Trial Network
        res = await client.post(
            "/api/v1/clinical-logistics/trials",
            json={
                "trial_protocol_number": "PROTO-TEST-API",
                "trial_title": "Test Phase III Global Network",
                "phase": "Phase III",
                "product_storage_regime": "Ultra-Cold Chain (-80°C)",
            },
        )
        assert res.status_code == 201
        data = res.json()
        trial_id = data["id"]
        assert len(data["sites"]) >= 4

        # 2. Get Trial Network Detail
        get_res = await client.get(f"/api/v1/clinical-logistics/trials/{trial_id}")
        assert get_res.status_code == 200
        assert get_res.json()["trial_protocol_number"] == "PROTO-TEST-API"

        # 3. List Trials
        list_res = await client.get("/api/v1/clinical-logistics/trials")
        assert list_res.status_code == 200
        assert any(t["id"] == trial_id for t in list_res.json())
