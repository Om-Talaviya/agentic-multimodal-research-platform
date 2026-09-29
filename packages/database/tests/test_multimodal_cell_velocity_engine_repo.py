"""Tests for Phase 347: Autonomous Single-Cell Multi-Modal Velocity (RNA+ATAC Dynamic Vector Field) Engine Repo."""

import pytest
from database.repositories.multimodal_cell_velocity_engine_repo import MultimodalCellVelocityEngineRepository


@pytest.mark.asyncio
async def test_multimodal_cell_velocity_engine_repository(db_session):
    repo = MultimodalCellVelocityEngineRepository(db_session)

    study = await repo.create_study(
        name="Study_347_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="multimodal-cell-velocity",
        lineage_trajectory_vector_field_coherence_pct=94.2,
        cell_fate_transition_probability_confidence_pct=96.8,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 347 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_347_Verification"
    assert getattr(study, "lineage_trajectory_vector_field_coherence_pct") == 94.2

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Hematopoietic_Stem_Cell_Multimodal_Lineage_Bifurcation_Field",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Hematopoietic_Stem_Cell_Multimodal_Lineage_Bifurcation_Field"

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
    assert fetched.name == "Study_347_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
