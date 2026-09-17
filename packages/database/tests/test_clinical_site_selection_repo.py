"""Tests for Clinical Site Selection repository."""
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from database.connection import Base
from database.repositories.clinical_site_selection_repo import ClinicalSiteSelectionRepository


@pytest.fixture
async def async_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_factory = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session_factory() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_create_and_get_study(async_session: AsyncSession):
    repo = ClinicalSiteSelectionRepository(async_session)

    study = await repo.create_study(
        study_title="Phase 3 Solid Tumor Trial",
        protocol_code="ST-301",
        indication="NSCLC",
        phase="Phase 3",
        target_enrollment=300,
        recruitment_duration_months=12.0,
        total_sites=2,
    )

    assert study.id is not None
    assert study.protocol_code == "ST-301"

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.study_title == "Phase 3 Solid Tumor Trial"


@pytest.mark.asyncio
async def test_add_sites_and_simulations(async_session: AsyncSession):
    repo = ClinicalSiteSelectionRepository(async_session)

    study = await repo.create_study(
        study_title="Phase 2 Melanoma Study",
        protocol_code="MEL-201",
        indication="Melanoma",
        phase="Phase 2",
        target_enrollment=150,
    )

    sites_data = [
        {
            "site_name": "Site Alpha",
            "country": "USA",
            "city": "Boston",
            "principal_investigator": "Dr. Smith",
            "historical_recruitment_rate": 3.0,
            "ethics_approval_timeline_days": 30,
            "patient_pool_density": 3000,
            "feasibility_score": 0.88,
            "risk_tier": "LOW_RISK",
            "selected_for_trial": True,
        },
        {
            "site_name": "Site Beta",
            "country": "Germany",
            "city": "Munich",
            "principal_investigator": "Dr. Weber",
            "historical_recruitment_rate": 1.5,
            "ethics_approval_timeline_days": 60,
            "patient_pool_density": 1500,
            "feasibility_score": 0.62,
            "risk_tier": "MODERATE_RISK",
            "selected_for_trial": True,
        }
    ]

    sites = await repo.add_sites(study.id, sites_data)
    assert len(sites) == 2

    sites_fetched = await repo.get_sites_by_study(study.id)
    assert len(sites_fetched) == 2
    assert sites_fetched[0].feasibility_score >= sites_fetched[1].feasibility_score

    sim = await repo.add_simulation(
        study_id=study.id,
        simulation_name="Monte Carlo Test Run",
        target_timeline_months=12.0,
        p10_completion_months=10.0,
        p50_completion_months=11.5,
        p90_completion_months=14.0,
        dropout_rate=0.10,
        enrollment_curve_json=[{"month": 1, "projected_enrolled": 10}],
        bottleneck_risks_json=[{"risk_type": "TIMELINE", "severity": "LOW"}],
    )
    assert sim.id is not None
    assert sim.p50_completion_months == 11.5

    sims = await repo.get_simulations_by_study(study.id)
    assert len(sims) == 1
