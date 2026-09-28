"""Tests for Phase 247: Autonomous Spatial Transcriptomics Cell-Cell Communication & Distance-Decay Ligand-Receptor Engine Repo."""

import pytest
from database.repositories.spatial_cell_cell_communication_repo import SpatialCellCellCommunicationRepository


@pytest.mark.asyncio
async def test_spatial_cell_cell_communication_repository(db_session):
    repo = SpatialCellCellCommunicationRepository(db_session)

    study = await repo.create_study(
        name="Study_247_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="spatial-cell-cell-communication",
        spatial_interaction_potential_score=89.6,
        distance_decay_effective_radius_um=45.0,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 247 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_247_Verification"
    assert getattr(study, "spatial_interaction_potential_score") == 89.6

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Glioblastoma_Tumor_Immune_Border_CXCL12_CXCR4_Niche",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Glioblastoma_Tumor_Immune_Border_CXCL12_CXCR4_Niche"

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
    assert fetched.name == "Study_247_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
