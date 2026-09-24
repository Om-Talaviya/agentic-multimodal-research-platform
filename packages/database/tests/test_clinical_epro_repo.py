"""Tests for ClinicalePRORepository."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from database.connection import Base
from database.repositories.clinical_epro_repo import ClinicalePRORepository


@pytest_asyncio.fixture
async def async_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        yield session
    await engine.dispose()


@pytest.mark.asyncio
async def test_clinical_epro_repo_lifecycle(async_db: AsyncSession):
    repo = ClinicalePRORepository(async_db)

    study = await repo.create_study(
        protocol_id="ONC-PH3-MELANOMA",
        therapeutic_area="Immuno-Oncology",
        patient_count=120,
        compliance_rate=0.942,
        composite_qol_score=0.81,
    )
    assert study.id is not None

    await repo.add_survey_telemetry(
        study_id=study.id,
        patient_pseudonym="PT-0091",
        visit_day=14,
        vas_pain_score=2.1,
        promis_fatigue_score=48.2,
        eq5d_utility_index=0.88,
    )

    await repo.add_adverse_event_alert(
        study_id=study.id,
        patient_pseudonym="PT-0091",
        ctcae_grade=3,
        symptom_name="Immune-Related Colitis",
        requires_site_escalation=True,
    )

    loaded = await repo.get_study_with_details(study.id)
    assert loaded is not None
    assert len(loaded.surveys) == 1
    assert len(loaded.adverse_events) == 1
    assert loaded.adverse_events[0].requires_site_escalation is True
