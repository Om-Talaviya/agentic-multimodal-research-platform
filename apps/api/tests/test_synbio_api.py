"""
Integration tests for Synthetic Biology REST API (Phase 65).
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
async def test_synbio_api_workflow(async_test_session: AsyncSession):
    async def override_get_db():
        yield async_test_session

    app.dependency_overrides[get_db_session] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Compile Circuit
        res = await client.post(
            "/api/v1/synthetic-biology/circuits",
            json={
                "circuit_name": "API Test AND Gate",
                "host_organism": "E. coli K-12",
                "logic_expression": "A AND B",
                "gate_topology": "AND Gate",
            },
        )
        assert res.status_code == 201
        data = res.json()
        circuit_id = data["id"]
        assert len(data["parts"]) >= 4

        # 2. Get Circuit Detail
        get_res = await client.get(f"/api/v1/synthetic-biology/circuits/{circuit_id}")
        assert get_res.status_code == 200
        assert get_res.json()["circuit_name"] == "API Test AND Gate"

        # 3. List Circuits
        list_res = await client.get("/api/v1/synthetic-biology/circuits")
        assert list_res.status_code == 200
        assert any(c["id"] == circuit_id for c in list_res.json())
