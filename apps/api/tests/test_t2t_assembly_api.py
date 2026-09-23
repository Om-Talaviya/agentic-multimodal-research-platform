"""
API integration tests for Phase 126: T2T Assembly & SV Calling Endpoints.
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
async def test_t2t_assembly_api_flow(test_app: AsyncClient):
    payload = {
        "sample_name": "HG002_T2T_Trial",
        "sequencing_technology": "PacBio-HiFi+ONT-UltraLong",
    }

    # 1. Assemble genome and call SVs
    res = await test_app.post("/api/v1/t2t-assembly/assemble", json=payload)
    assert res.status_code == 201, res.text
    data = res.json()
    assert data["status"] == "success"
    assert "assembly_id" in data
    assembly_id = data["assembly_id"]
    assert data["variants_count"] >= 4
    assert data["haplotypes_count"] >= 2

    # 2. List assemblies
    list_res = await test_app.get("/api/v1/t2t-assembly/assemblies")
    assert list_res.status_code == 200
    assemblies = list_res.json()
    assert any(a["id"] == assembly_id for a in assemblies)

    # 3. Retrieve single assembly
    get_res = await test_app.get(f"/api/v1/t2t-assembly/assemblies/{assembly_id}")
    assert get_res.status_code == 200
    detail = get_res.json()
    assert detail["sample_name"] == "HG002_T2T_Trial"
    assert len(detail["variants"]) >= 4
    assert len(detail["haplotypes"]) >= 2
