"""Tests for Phase 235: Autonomous Cryo-EM Symmetry-Mismatch & Helical Filament Reconstruction Engine Repo."""

import pytest
from database.repositories.cryoem_symmetry_mismatch_refine_repo import CryoEMSymmetryMismatchRefineRepository


@pytest.mark.asyncio
async def test_cryoem_symmetry_mismatch_refine_repository(db_session):
    repo = CryoEMSymmetryMismatchRefineRepository(db_session)

    study = await repo.create_study(
        name="Study_235_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="cryoem-symmetry-mismatch-refine",
        helical_pitch_rise_angstrom=4.75,
        symmetry_deconvolution_fsc_angstrom=2.85,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 235 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_235_Verification"
    assert getattr(study, "helical_pitch_rise_angstrom") == 4.75

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Tau_Paired_Helical_Filament_Alzheimer_Brain",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Tau_Paired_Helical_Filament_Alzheimer_Brain"

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
    assert fetched.name == "Study_235_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
