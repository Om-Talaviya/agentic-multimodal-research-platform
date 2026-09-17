"""Tests for Pharmacovigilance Signal Mining repository."""
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from database.connection import Base
from database.repositories.pv_signal_mining_repo import PVSignalMiningRepository


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
    repo = PVSignalMiningRepository(async_session)

    study = await repo.create_study(
        study_name="FAERS Statin Study",
        drug_name="Atorvastatin",
        active_substance="HMG-CoA Reductase Inhibitor",
        target_adverse_event="Rhabdomyolysis",
        data_source="FAERS",
        total_cases_analyzed=50000,
        signal_status="CONFIRMED_SIGNAL",
        who_causality_grade="PROBABLE",
    )

    assert study.id is not None
    assert study.drug_name == "Atorvastatin"

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.signal_status == "CONFIRMED_SIGNAL"


@pytest.mark.asyncio
async def test_add_metrics_and_cases(async_session: AsyncSession):
    repo = PVSignalMiningRepository(async_session)

    study = await repo.create_study(
        study_name="ICI Myocarditis Sentinel",
        drug_name="Pembrolizumab",
        active_substance="Anti-PD-1",
        target_adverse_event="Myocarditis",
    )

    metrics_data = [
        {
            "metric_name": "PRR",
            "value": 12.5,
            "confidence_interval_lower": 9.2,
            "confidence_interval_upper": 16.8,
            "is_statistically_significant": True,
            "threshold_exceeded": True,
        },
        {
            "metric_name": "IC025",
            "value": 2.9,
            "confidence_interval_lower": 2.9,
            "confidence_interval_upper": 3.8,
            "is_statistically_significant": True,
            "threshold_exceeded": True,
        }
    ]

    metrics = await repo.add_metrics(study.id, metrics_data)
    assert len(metrics) == 2

    cases_data = [
        {
            "report_id": "CASE-101",
            "patient_age": 62,
            "patient_gender": "Male",
            "primary_suspect_drug": "Pembrolizumab",
            "concomitant_drugs_json": ["Metformin"],
            "adverse_event_term": "Myocarditis",
            "meddra_soc": "Cardiac disorders",
            "time_to_onset_days": 15,
            "outcome": "HOSPITALIZATION",
        }
    ]

    cases = await repo.add_case_reports(study.id, cases_data)
    assert len(cases) == 1

    fetched_metrics = await repo.get_metrics_by_study(study.id)
    assert len(fetched_metrics) == 2

    fetched_cases = await repo.get_cases_by_study(study.id)
    assert len(fetched_cases) == 1
