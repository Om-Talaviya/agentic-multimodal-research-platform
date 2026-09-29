"""Tests for Phase 342: Autonomous Ultra-High Content High-Throughput Organoid Drug Screening Phenotypic Profiler Repo."""

import pytest
from database.repositories.organoid_phenotypic_profiler_repo import OrganoidPhenotypicProfilerRepository


@pytest.mark.asyncio
async def test_organoid_phenotypic_profiler_repository(db_session):
    repo = OrganoidPhenotypicProfilerRepository(db_session)

    study = await repo.create_study(
        name="Study_342_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="organoid-phenotypic-profiler",
        high_throughput_z_prime_factor=0.86,
        organoid_lumen_swelling_rate_pct_hr=34.2,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 342 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_342_Verification"
    assert getattr(study, "high_throughput_z_prime_factor") == 0.86

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Patient_Derived_Colorectal_Organoid_5000_Compound_Screen",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Patient_Derived_Colorectal_Organoid_5000_Compound_Screen"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="Sensitivity & Recovery Rate",
        observed_value=0.984,
        z_score=2.85,
        p_value=0.00012,
    )
    assert trace.id is not None
    assert trace.observed_value == 0.984

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_342_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
