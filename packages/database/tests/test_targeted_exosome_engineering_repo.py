"""Tests for Phase 373: Autonomous Targeted Exosome Surface Engineering & Blood-Brain Barrier Transcytosis Simulator Repo."""

import pytest
from database.repositories.targeted_exosome_engineering_repo import TargetedExosomeEngineeringRepository


@pytest.mark.asyncio
async def test_targeted_exosome_engineering_repository(db_session):
    repo = TargetedExosomeEngineeringRepository(db_session)

    study = await repo.create_study(
        name="Study_373_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="targeted-exosome-engineering",
        blood_brain_barrier_transcytosis_rate_pct=18.2,
        vesicle_colloidal_stability_zeta_potential_mv=28.5,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 373 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_373_Verification"
    assert getattr(study, "blood_brain_barrier_transcytosis_rate_pct") == 18.2

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="RVG_Peptide_Display_Engineered_HEK293_Exosome_Pool",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "RVG_Peptide_Display_Engineered_HEK293_Exosome_Pool"

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
    assert fetched.name == "Study_373_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
