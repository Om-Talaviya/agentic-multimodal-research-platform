"""Tests for Phase 296: Autonomous Targeted Prime-Editing PegRNA-Engineered Flap Resolution & Microhomology Suppression Matrix Repo."""

import pytest
from database.repositories.prime_editing_flap_resolution_repo import PrimeEditingFlapResolutionRepository


@pytest.mark.asyncio
async def test_prime_editing_flap_resolution_repository(db_session):
    repo = PrimeEditingFlapResolutionRepository(db_session)

    study = await repo.create_study(
        name="Study_296_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="prime-editing-flap-resolution",
        prime_editing_precise_insertion_purity_pct=96.5,
        microhomology_indel_suppression_fold=8.2,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 296 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_296_Verification"
    assert getattr(study, "prime_editing_precise_insertion_purity_pct") == 96.5

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Sickle_Cell_HBB_Glu6Val_Prime_Flap_Optimizer",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Sickle_Cell_HBB_Glu6Val_Prime_Flap_Optimizer"

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
    assert fetched.name == "Study_296_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
