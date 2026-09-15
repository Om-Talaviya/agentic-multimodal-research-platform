"""Unit tests for Clinical Trial Repository (Phase 46)."""
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from database.connection import Base
from database.repositories.clinical_trial_repo import ClinicalTrialRepository

@pytest.fixture
async def async_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        yield session
    
    await engine.dispose()

@pytest.mark.asyncio
async def test_clinical_trial_repo_crud(async_session: AsyncSession):
    repo = ClinicalTrialRepository(async_session)
    protocol = await repo.create_protocol(
        title="Phase II NSCLC AGY-801 Study",
        phase="Phase II",
        target_indication="Non-Small Cell Lung Cancer",
        investigational_agent="AGY-801",
        primary_endpoint="Overall Survival",
        sample_size_target=140
    )
    assert protocol.id is not None
    assert protocol.status == "OPTIMIZED"

    crit = await repo.add_criteria(
        protocol_id=protocol.id,
        criterion_type="INCLUSION",
        description="Histologically confirmed Stage IV NSCLC",
        category="CLINICAL"
    )
    assert crit.id is not None

    arm = await repo.create_synthetic_control_arm(
        protocol_id=protocol.id,
        rwe_data_source="EHR Flatiron",
        baseline_patient_count=500,
        matched_patient_count=140,
        median_os_control=9.5,
        median_os_interventional=17.2,
        p_value=0.001,
        hazard_ratio=0.58,
        survival_curve=[{"month": 0, "control_survival": 1.0, "interventional_survival": 1.0}]
    )
    assert arm.id is not None

    fetched = await repo.get_protocol(protocol.id)
    assert len(fetched.eligibility_criteria) == 1
    assert len(fetched.synthetic_arms) == 1
