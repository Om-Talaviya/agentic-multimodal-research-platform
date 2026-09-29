"""Tests for Phase 279: Autonomous Dynamic Single-Cell RNA Velocity & Optimal Transport Lineage Trajectory Engine Repo."""

import pytest
from database.repositories.sc_velocity_optimal_transport_repo import ScVelocityOptimalTransportRepository


@pytest.mark.asyncio
async def test_sc_velocity_optimal_transport_repository(db_session):
    repo = ScVelocityOptimalTransportRepository(db_session)

    study = await repo.create_study(
        name="Study_279_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="sc-velocity-optimal-transport",
        cell_fate_transition_coupling_confidence=94.2,
        rna_velocity_confidence_score=0.88,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 279 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_279_Verification"
    assert getattr(study, "cell_fate_transition_coupling_confidence") == 94.2

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Glioblastoma_Stem_Cell_Differentiation_Vector_Field",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Glioblastoma_Stem_Cell_Differentiation_Vector_Field"

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
    assert fetched.name == "Study_279_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
