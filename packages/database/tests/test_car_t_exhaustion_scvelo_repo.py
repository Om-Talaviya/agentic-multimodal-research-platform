"""Tests for Phase 220: Autonomous Single-Cell RNA Velocity Lineage Trajectory & CAR-T Epigenetic Exhaustion Interceptor Engine Repo."""

import pytest
from database.repositories.car_t_exhaustion_scvelo_repo import CarTExhaustionScveloRepository


@pytest.mark.asyncio
async def test_car_t_exhaustion_scvelo_repository(db_session):
    repo = CarTExhaustionScveloRepository(db_session)

    study = await repo.create_study(
        name="Study_220_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="car-t-exhaustion-scvelo",
        exhaustion_diversion_efficiency_pct=92.8,
        stem_memory_persistence_index=0.89,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 220 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_220_Verification"
    assert getattr(study, "exhaustion_diversion_efficiency_pct") == 92.8

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="CD19_CAR_T_Day14_SplicedRNA_Trajectory",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "CD19_CAR_T_Day14_SplicedRNA_Trajectory"

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
    assert fetched.name == "Study_220_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
