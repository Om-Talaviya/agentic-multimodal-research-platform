"""Integration tests for Clinical Trial Protocol & Drug Repurposing API (Phase 36)."""

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
        username="lead_investigator",
        email="pi@precision-oncology.org",
        password_hash="mocked",
        role="Researcher",
    )


@pytest.mark.asyncio
async def test_clinical_trials_api_full_workflow(async_test_session: AsyncSession, mock_user: DBUser):
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
        # 1. Generate clinical protocol
        gen_payload = {
            "disease_indication": "Transthyretin Amyloidosis (ATTR)",
            "investigational_agent": "NTLA-2001 LNP-Cas9",
            "target_gene_or_protein": "TTR",
            "phase_type": "Phase I/IIa",
            "mechanism_of_action": "Targeted TTR exon disruption for systemic amyloid reduction",
        }
        res = await client.post("/api/v1/clinical/protocols/generate", json=gen_payload)
        assert res.status_code == 201, res.text
        data = res.json()
        assert "protocol_id" in data
        proto_id = data["protocol_id"]
        assert data["disease_indication"] == "Transthyretin Amyloidosis (ATTR)"
        assert data["cohort_criteria_count"] >= 6
        assert data["drug_candidates_count"] >= 2

        # 2. List protocols
        list_res = await client.get("/api/v1/clinical/protocols")
        assert list_res.status_code == 200
        list_data = list_res.json()
        assert list_data["total"] >= 1
        assert list_data["protocols"][0]["id"] == proto_id

        # 3. Get protocol details
        detail_res = await client.get(f"/api/v1/clinical/protocols/{proto_id}")
        assert detail_res.status_code == 200
        detail_data = detail_res.json()
        assert detail_data["id"] == proto_id
        assert len(detail_data["cohort_criteria"]) >= 6
        assert len(detail_data["drug_candidates"]) >= 2
        assert len(detail_data["regulatory_packages"]) >= 1

        # 4. Add custom cohort criterion
        crit_payload = {
            "criterion_type": "exclusion",
            "category": "safety",
            "description": "Platelet count < 75,000/mcL or international normalized ratio (INR) > 1.5.",
            "is_mandatory": True,
        }
        crit_res = await client.post(f"/api/v1/clinical/protocols/{proto_id}/criteria", json=crit_payload)
        assert crit_res.status_code == 201
        assert crit_res.json()["criterion_type"] == "exclusion"

        # 5. Generate EMA CTD regulatory package
        reg_payload = {"regulatory_agency": "EMA"}
        reg_res = await client.post(f"/api/v1/clinical/protocols/{proto_id}/regulatory-package", json=reg_payload)
        assert reg_res.status_code == 201
        reg_data = reg_res.json()
        assert reg_data["regulatory_agency"] == "EMA"
        assert reg_data["completeness_score"] >= 0.85

    app.dependency_overrides.clear()
