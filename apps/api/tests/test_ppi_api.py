"""
Integration tests for PPI Interactome REST API (Phase 58).
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
async def test_ppi_api_workflow(async_test_session: AsyncSession):
    async def override_get_db():
        yield async_test_session

    app.dependency_overrides[get_db_session] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Create Network
        res = await client.post(
            "/api/v1/ppi-interactome/networks",
            json={
                "network_name": "Test KRAS Network",
                "seed_gene": "KRAS",
                "disease_context": "Lung Adenocarcinoma",
            },
        )
        assert res.status_code == 201
        data = res.json()
        net_id = data["id"]
        assert len(data["nodes"]) >= 5
        assert len(data["edges"]) >= 5

        # 2. Get Network Detail
        get_res = await client.get(f"/api/v1/ppi-interactome/networks/{net_id}")
        assert get_res.status_code == 200
        assert get_res.json()["network_name"] == "Test KRAS Network"

        # 3. List Networks
        list_res = await client.get("/api/v1/ppi-interactome/networks")
        assert list_res.status_code == 200
        assert any(n["id"] == net_id for n in list_res.json())
