"""Tests for Phase 401: Autonomous Magnetic Tweezers Single-Molecule DNA Supercoiling Engine Repo."""

import pytest
from database.repositories.magnetic_tweezers_dna_supercoiling_repo import MagneticTweezersDnaSupercoilingRepository


@pytest.mark.asyncio
async def test_magnetic_tweezers_dna_supercoiling_repository(db_session):
    repo = MagneticTweezersDnaSupercoilingRepository(db_session)

    study = await repo.create_study(
        name="Study_401_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="magnetic-tweezers-dna-supercoiling",
        dna_extension_change_nm_per_turn=52.4,
        topoisomerase_relaxation_unlinking_rate_hz=8.75,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 401 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_401_Verification"
    assert getattr(study, "dna_extension_change_nm_per_turn") == 52.4

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Paramagnetic_Bead_Tethered_Double_Stranded_DNA_Substrate",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Paramagnetic_Bead_Tethered_Double_Stranded_DNA_Substrate"

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
    assert fetched.name == "Study_401_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
