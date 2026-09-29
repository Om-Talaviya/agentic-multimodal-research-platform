"""Tests for Phase 267: Autonomous In-Vivo CAR-T Cell In-Situ Reprogramming & Retargeting Tropism Vector Simulator Repo."""

import pytest
from database.repositories.in_vivo_cart_reprogramming_tropism_repo import InVivoCartReprogrammingTropismRepository


@pytest.mark.asyncio
async def test_in_vivo_cart_reprogramming_tropism_repository(db_session):
    repo = InVivoCartReprogrammingTropismRepository(db_session)

    study = await repo.create_study(
        name="Study_267_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="in-vivo-cart-reprogramming-tropism",
        in_vivo_t_cell_transduction_selectivity_fold=42.5,
        hepatic_off_target_accumulation_reduction_pct=88.6,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 267 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_267_Verification"
    assert getattr(study, "in_vivo_t_cell_transduction_selectivity_fold") == 42.5

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Anti_CD5_Targeted_LNP_In_Vivo_CAR_T_Delivery",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Anti_CD5_Targeted_LNP_In_Vivo_CAR_T_Delivery"

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
    assert fetched.name == "Study_267_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
