"""Tests for Phase 284: Autonomous In-Silico High-Dimensional CyTOF Spectral Unmixing & Mass Tag Cross-Talk Compensator Repo."""

import pytest
from database.repositories.cytof_spectral_unmixing_compensator_repo import CytofSpectralUnmixingCompensatorRepository


@pytest.mark.asyncio
async def test_cytof_spectral_unmixing_compensator_repository(db_session):
    repo = CytofSpectralUnmixingCompensatorRepository(db_session)

    study = await repo.create_study(
        name="Study_284_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="cytof-spectral-unmixing-compensator",
        signal_spillover_reduction_ratio_pct=98.6,
        single_cell_channel_cross_talk_residual=0.02,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 284 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_284_Verification"
    assert getattr(study, "signal_spillover_reduction_ratio_pct") == 98.6

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="50_Plex_Immune_Exhaustion_CyTOF_Spillover_Matrix",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "50_Plex_Immune_Exhaustion_CyTOF_Spillover_Matrix"

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
    assert fetched.name == "Study_284_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
