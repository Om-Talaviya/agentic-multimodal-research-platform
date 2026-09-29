"""Tests for Phase 344: Autonomous Lipid Nanoparticle (LNP) In Vivo Endosomal Escape & Cytosolic Release Efficiency Predictor Repo."""

import pytest
from database.repositories.lnp_endosomal_escape_predictor_repo import LnpEndosomalEscapePredictorRepository


@pytest.mark.asyncio
async def test_lnp_endosomal_escape_predictor_repository(db_session):
    repo = LnpEndosomalEscapePredictorRepository(db_session)

    study = await repo.create_study(
        name="Study_344_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="lnp-endosomal-escape",
        endosomal_escape_fractional_efficiency_pct=8.4,
        cytosolic_mrna_translation_half_life_hr=28.5,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 344 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_344_Verification"
    assert getattr(study, "endosomal_escape_fractional_efficiency_pct") == 8.4

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Ionizable_Lipid_pKa_6_4_Endosomal_Hexagonal_Transition_Matrix",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Ionizable_Lipid_pKa_6_4_Endosomal_Hexagonal_Transition_Matrix"

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
    assert fetched.name == "Study_344_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
