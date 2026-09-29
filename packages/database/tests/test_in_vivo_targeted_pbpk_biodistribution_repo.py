"""Tests for Phase 328: Autonomous Whole-Body Physiologically-Based Pharmacokinetic (PBPK) Nanomedicine Bio-Distribution & Clearance Modeler Repo."""

import pytest
from database.repositories.in_vivo_targeted_pbpk_biodistribution_repo import InVivoTargetedPbpkBiodistributionRepository


@pytest.mark.asyncio
async def test_in_vivo_targeted_pbpk_biodistribution_repository(db_session):
    repo = InVivoTargetedPbpkBiodistributionRepository(db_session)

    study = await repo.create_study(
        name="Study_328_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="in-vivo-targeted-pbpk",
        pbpk_plasma_tissue_concentration_auc_accuracy_pct=96.2,
        tumor_to_blood_exposure_ratio_fold=14.8,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 328 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_328_Verification"
    assert getattr(study, "pbpk_plasma_tissue_concentration_auc_accuracy_pct") == 96.2

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Antibody_Oligonucleotide_Conjugate_AOC_Whole_Body_PBPK_Simulation",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Antibody_Oligonucleotide_Conjugate_AOC_Whole_Body_PBPK_Simulation"

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
    assert fetched.name == "Study_328_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
