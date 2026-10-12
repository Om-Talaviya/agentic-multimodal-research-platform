"""Tests for Phase 416: Autonomous Optical Tweezers DNA-Protein Mechanical Tension & Force-Extension Overstretching Modeler Repo."""

import pytest
from database.repositories.optical_tweezers_dna_mechanics_repo import OpticalTweezersDnaMechanicsRepository


@pytest.mark.asyncio
async def test_optical_tweezers_dna_mechanics_repository(db_session):
    repo = OpticalTweezersDnaMechanicsRepository(db_session)

    study = await repo.create_study(
        name="Study_416_Verification",
        target_specimen="Single-Molecule Lambda-DNA Tether with RecA Nucleoprotein",
        analytical_modality="optical-tweezers",
        overstretching_transition_force_pN=65.4,
        persistence_length_nm=47.8,
        contour_length_um=16.2,
        trap_stiffness_pN_per_nm=0.185,
        confidence_score=0.991,
        status="completed",
        summary_report="Phase 416 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_416_Verification"
    assert study.overstretching_transition_force_pN == 65.4

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Worm_Like_Chain_Overstretching_Plateau",
        profile_category="Primary Step",
        quantitative_value=65.4,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Worm_Like_Chain_Overstretching_Plateau"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="overstretching_transition_force_pN",
        observed_value=65.4,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 65.4

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_416_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
