"""Tests for Phase 388: Autonomous High-Content Organoid Electrophysiology Micro-Capillary Patch-Clamp Analyzer Repo."""

import pytest
from database.repositories.organoid_patch_clamp_analyzer_repo import OrganoidPatchClampAnalyzerRepository


@pytest.mark.asyncio
async def test_organoid_patch_clamp_analyzer_repository(db_session):
    repo = OrganoidPatchClampAnalyzerRepository(db_session)

    study = await repo.create_study(
        name="Study_388_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="organoid-patch-clamp-analyzer",
        action_potential_amplitude_millivolts=95.0,
        whole_cell_gigaseal_formation_success_pct=92.5,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 388 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_388_Verification"
    assert getattr(study, "action_potential_amplitude_millivolts") == 95.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Human_Cerebral_Organoid_Pyramidal_Neuron_Whole_Cell_Recording",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Human_Cerebral_Organoid_Pyramidal_Neuron_Whole_Cell_Recording"

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
    assert fetched.name == "Study_388_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
