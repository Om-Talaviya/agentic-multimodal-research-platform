"""Integration tests for CRISPR & Synthetic Biology Guide RNA Design API (Phase 40)."""

import uuid
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from api.dependencies import get_current_user, get_db_session
from database.connection import Base
from database.models.user import User as DBUser
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
        username="crispr_engineer",
        email="crispr@broadinstitute.org",
        password_hash="mocked",
        role="Researcher",
    )


@pytest.mark.asyncio
async def test_crispr_api_workflow(async_test_session: AsyncSession, mock_user: DBUser):
    async_test_session.add(mock_user)
    await async_test_session.commit()

    async def override_get_db():
        yield async_test_session

    async def override_get_user():
        return mock_user

    app.dependency_overrides[get_db_session] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_user

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. POST /api/v1/crispr/design
        payload = {
            "target_gene": "PCSK9",
            "target_sequence": "ATGGGCACCGTCAGCTCCAGGCGGTCCTGGTGGCCGCTGCCACTGCTGCTGCTGCTGCTGCTGCTCCTGGGTCCCGCGGGCGCCCGTGCGCAGGAGGACGAGGACGGCGACTACGAGGAGCTGGTGCTAGCCTTGCGTTCCGAGGAGGACGGCCTGGCCGAAGCACCCGAGCACGGAACCACAGCCACCTTCCACCGCTGCGCCAAGGATCCGTGGCGGTTGCCCGGCACCTAC",
            "cas_type": "SpCas9",
            "organism": "Homo sapiens",
            "description": "PCSK9 Exon 1 CRISPR Targeting",
            "max_guides": 5,
        }
        res = await client.post("/api/v1/crispr/design", json=payload)
        assert res.status_code == 201
        data = res.json()
        assert data["target_gene"] == "PCSK9"
        assert len(data["guides"]) > 0
        design_id = data["design_id"]
        guide_id = data["guides"][0]["id"]

        # 2. GET /api/v1/crispr/designs
        res = await client.get("/api/v1/crispr/designs")
        assert res.status_code == 200
        assert res.json()["count"] >= 1

        # 3. GET /api/v1/crispr/designs/{id}
        res = await client.get(f"/api/v1/crispr/designs/{design_id}")
        assert res.status_code == 200
        design_detail = res.json()
        assert design_detail["id"] == design_id
        assert len(design_detail["guides"]) > 0
        assert len(design_detail["guides"][0]["off_targets"]) > 0
        assert len(design_detail["guides"][0]["base_editing_profiles"]) > 0

        # 4. GET /api/v1/crispr/guides/{id}/oligos
        res = await client.get(f"/api/v1/crispr/guides/{guide_id}/oligos")
        assert res.status_code == 200
        oligo_data = res.json()
        assert oligo_data["top_oligo"]["sequence"].startswith("CACC")
        assert oligo_data["bottom_oligo"]["sequence"].startswith("AAAC")

        # 5. GET /api/v1/crispr/designs/{id}/export-genbank
        res = await client.get(f"/api/v1/crispr/designs/{design_id}/export-genbank")
        assert res.status_code == 200
        assert "LOCUS" in res.text
        assert "ORIGIN" in res.text

        # 6. DELETE /api/v1/crispr/designs/{id}
        res = await client.delete(f"/api/v1/crispr/designs/{design_id}")
        assert res.status_code == 200
        assert res.json()["status"] == "deleted"

    app.dependency_overrides.clear()
