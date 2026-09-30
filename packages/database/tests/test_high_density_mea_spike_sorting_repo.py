"""Tests for Phase 410: High-Density MEA Real-Time Neuromorphic Action Potential Spike Sorter Repo."""

import pytest
from database.repositories.high_density_mea_spike_sorting_repo import HighDensityMeaSpikeSortingRepository


@pytest.mark.asyncio
async def test_high_density_mea_spike_sorting_repository(db_session):
    repo = HighDensityMeaSpikeSortingRepository(db_session)

    study = await repo.create_study(
        name="Study_410_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="high-density-mea-spike-sorting",
        spike_sorting_single_unit_isolation_f1_score=0.945,
        realtime_neuromorphic_processing_latency_us=85.0,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 410 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_410_Verification"
    assert getattr(study, "spike_sorting_single_unit_isolation_f1_score") == 0.945

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="CMOS_HD_MEA_4096_Channel_Microelectrode_Array_Mesh",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "CMOS_HD_MEA_4096_Channel_Microelectrode_Array_Mesh"

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
    assert fetched.name == "Study_410_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
