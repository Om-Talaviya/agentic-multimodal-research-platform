"""Tests for Phase 316: Autonomous Time-Resolved Cryo-EM Sub-Millisecond Microfluidic Jet Conformational State Classifier Repo."""

import pytest
from database.repositories.cryoem_time_resolved_ensemble_repo import CryoemTimeResolvedEnsembleRepository


@pytest.mark.asyncio
async def test_cryoem_time_resolved_ensemble_repository(db_session):
    repo = CryoemTimeResolvedEnsembleRepository(db_session)

    study = await repo.create_study(
        name="Study_316_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="cryoem-time-resolved-ensemble",
        structural_intermediate_resolution_angstroms=2.1,
        microfluidic_mixing_dead_time_ms=2.85,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 316 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_316_Verification"
    assert getattr(study, "structural_intermediate_resolution_angstroms") == 2.1

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Ribosome_Elongation_GTP_Hydrolysis_Intermediate_CryoEM_Trajectory",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Ribosome_Elongation_GTP_Hydrolysis_Intermediate_CryoEM_Trajectory"

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
    assert fetched.name == "Study_316_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
