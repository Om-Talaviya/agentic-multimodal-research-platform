"""Tests for ClinicalRepository (Phase 36)."""

import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from database.connection import Base
from database.models.user import User as DBUser
from database.repositories.clinical_repo import ClinicalRepository


@pytest.fixture
async def test_db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_clinical_repo_full_lifecycle(test_db_session: AsyncSession):
    repo = ClinicalRepository(test_db_session)
    user_id = uuid.uuid4()

    # Create dummy user
    user = DBUser(id=user_id, username="test_clinician", email="clinician@hospital.org", password_hash="hash")
    test_db_session.add(user)
    await test_db_session.commit()

    # 1. Create Protocol
    protocol = await repo.create_protocol(
        user_id=user_id,
        protocol_title="Phase I/IIa Study of LNP-Cas9 in FH",
        disease_indication="Familial Hypercholesterolemia",
        investigational_agent="LNP-Cas9-PCSK9",
        primary_endpoint="Incidence of TEAEs through Week 24",
        phase_type="Phase I/IIa",
        target_gene_or_protein="PCSK9",
        sample_size_planned=48,
        adverse_risk_score=0.14,
    )
    assert protocol.id is not None
    assert protocol.protocol_title == "Phase I/IIa Study of LNP-Cas9 in FH"

    # 2. Add Cohort Criteria
    crit1 = await repo.add_cohort_criterion(
        protocol_id=protocol.id,
        criterion_type="inclusion",
        description="Adult patients aged 18-75 with confirmed diagnosis.",
        category="demographic",
    )
    crit2 = await repo.add_cohort_criterion(
        protocol_id=protocol.id,
        criterion_type="exclusion",
        description="Severe hepatic impairment.",
        category="safety",
    )
    assert crit1.criterion_type == "inclusion"
    assert crit2.criterion_type == "exclusion"

    # 3. Add Drug Candidate
    candidate = await repo.add_drug_candidate(
        protocol_id=protocol.id,
        compound_name="Atorvastatin Co-Formulation",
        current_approved_indication="Hypercholesterolemia",
        repurposed_indication="Synergistic Hepatic Clearance",
        repurposing_rationale="Upstream HMGCR pathway suppression",
        binding_affinity_nm=8.4,
    )
    assert candidate.compound_name == "Atorvastatin Co-Formulation"

    # 4. Create Regulatory Package
    reg_pkg = await repo.create_regulatory_package(
        protocol_id=protocol.id,
        regulatory_agency="FDA",
        module_type="IND Module 2",
        completeness_score=0.94,
        irb_readiness_verdict="ready",
    )
    assert reg_pkg.completeness_score == 0.94
    assert reg_pkg.irb_readiness_verdict == "ready"

    await test_db_session.commit()

    # 5. Fetch and verify relationships
    fetched = await repo.get_protocol(protocol.id)
    assert fetched is not None
    assert len(fetched.cohort_criteria) == 2
    assert len(fetched.drug_candidates) == 1
    assert len(fetched.regulatory_packages) == 1

    # 6. List protocols
    protocols_list = await repo.list_protocols(user_id=user_id)
    assert len(protocols_list) == 1
    assert protocols_list[0].id == protocol.id
