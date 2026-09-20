"""
API integration tests for Phase 104: Immune Repertoire & TCR/BCR Clonotype Endpoints.
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
async def test_immune_repertoire_api_flow(test_app: AsyncClient):
    # 1. Post analysis
    payload = {
        "sample_name": "API-TCR-Sample",
        "organism": "Homo sapiens",
        "chain_type": "TCR_ALPHA_BETA",
        "clonotypes": [
            {
                "cdr3_aa": "CASSLAPGATNEKLFF",
                "v_gene": "TRBV7-2*01",
                "j_gene": "TRBJ1-4*01",
                "count": 700,
                "is_productive": True
            },
            {
                "cdr3_aa": "CASSLIGVSSYNEQFF",
                "v_gene": "TRBV19*01",
                "j_gene": "TRBJ2-1*01",
                "count": 300,
                "is_productive": True
            }
        ]
    }

    res = await test_app.post("/api/v1/immune-repertoire/analyze", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["sample_name"] == "API-TCR-Sample"
    assert data["clonotype_count"] == 2
    assert data["total_cells"] == 1000
    assert len(data["clonotypes"]) == 2
    assert len(data["vdj_pairings"]) == 2
    rep_id = data["id"]

    # 2. List repertoires
    list_res = await test_app.get("/api/v1/immune-repertoire/repertoires")
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert len(list_data) >= 1

    # 3. Get detail
    detail_res = await test_app.get(f"/api/v1/immune-repertoire/repertoires/{rep_id}")
    assert detail_res.status_code == 200
    detail_data = detail_res.json()
    assert detail_data["id"] == rep_id
    assert detail_data["clonotypes"][0]["antigen_specificity"] is not None
