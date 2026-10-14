"""Tests for Phase 489: Autonomous Multicellular Epithelial-to-Mesenchymal Transition (EMT) Snail-Twist Continuum Engine Repo."""

import pytest
from database.repositories.emt_snail_twist_continuum_repo import EmtSnailTwistContinuumRepository


@pytest.mark.asyncio
async def test_emt_snail_twist_continuum_repository(db_session):
    repo = EmtSnailTwistContinuumRepository(db_session)

    study = await repo.create_study(
        name="Study_489_Verification",
        target_specimen="TGF-beta Stimulated Mammary Epithelial MCF-10A Monolayer with Fluorescent E-Cadherin / Vimentin",
        analytical_modality="emt-snail-twist-continuum",
        e_cadherin_vimentin_expression_ratio=0.42,
        intermediate_hybrid_state_fraction=0.38,
        snail1_nuclear_translocation_tau_hours=14.5,
        mesenchymal_migration_velocity_um_per_hr=24.8,
        confidence_score=0.991,
        status="completed",
        summary_report="Phase 489 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_489_Verification"
    assert study.e_cadherin_vimentin_expression_ratio == 0.42

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="E_to_M_Partial_Hybrid_State_Landscape",
        profile_category="Primary Step",
        quantitative_value=0.42,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "E_to_M_Partial_Hybrid_State_Landscape"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="e_cadherin_vimentin_expression_ratio",
        observed_value=0.42,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 0.42

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_489_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
