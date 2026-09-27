"""Tests for Phase 239: Autonomous Single-Molecule Optical Tweezers & AFM Force-Induced Unfolding Kinetics Engine Repo."""

import pytest
from database.repositories.single_molecule_force_spectroscopy_repo import SingleMoleculeForceSpectroscopyRepository


@pytest.mark.asyncio
async def test_single_molecule_force_spectroscopy_repository(db_session):
    repo = SingleMoleculeForceSpectroscopyRepository(db_session)

    study = await repo.create_study(
        name="Study_239_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="single-molecule-force-spectroscopy",
        rupture_force_pico_newtons=165.4,
        transition_state_distance_angstrom=3.8,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 239 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_239_Verification"
    assert getattr(study, "rupture_force_pico_newtons") == 165.4

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Titin_Immunoglobulin_I27_Domain_Unfolding_Arc",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Titin_Immunoglobulin_I27_Domain_Unfolding_Arc"

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
    assert fetched.name == "Study_239_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
