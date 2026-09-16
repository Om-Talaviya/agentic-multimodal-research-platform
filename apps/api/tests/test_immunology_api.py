"""Integration tests for Computational Immunology REST API (Phase 55)."""
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from api.dependencies import get_db_session
from database.connection import Base
from main import app


@pytest.fixture
async def async_test_session():
    """Create in-memory SQLite database session for API integration tests."""
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
async def test_immunology_api_full_workflow(async_test_session: AsyncSession):
    async def override_get_db():
        yield async_test_session

    app.dependency_overrides[get_db_session] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Create Screen
        res = await client.post(
            "/api/v1/immunology/screens",
            json={
                "patient_id": "PT-TEST-001",
                "tumor_type": "Melanoma",
                "hla_alleles": ["HLA-A*02:01"],
                "mutations": [
                    {
                        "gene_symbol": "BRAF",
                        "mutation_variant": "V600E",
                        "peptide_sequence": "EDLTVKIGD",
                    }
                ],
            },
        )
        assert res.status_code == 200
        data = res.json()
        screen_id = data["id"]
        assert len(data["epitopes"]) >= 1

        # 2. Get Screen Detail
        get_res = await client.get(f"/api/v1/immunology/screens/{screen_id}")
        assert get_res.status_code == 200
        assert get_res.json()["patient_id"] == "PT-TEST-001"

        # 3. List Screens
        list_res = await client.get("/api/v1/immunology/screens")
        assert list_res.status_code == 200
        assert any(s["id"] == screen_id for s in list_res.json())

        # 4. Design Vaccine
        res_vax = await client.post(
            f"/api/v1/immunology/screens/{screen_id}/design-vaccine",
            json={
                "construct_name": "TestVax",
                "construct_type": "mRNA_LNP",
                "linker": "AAY",
            },
        )
        assert res_vax.status_code == 200
        assert "full_polyepitope_sequence" in res_vax.json()
