"""Tests for Phase 318: Autonomous Artificial Biomimetic Solid-State Nanopore Ion-Channel Gating & Selectivity Predictor Repo."""

import pytest
from database.repositories.biomimetic_ion_channel_gating_repo import BiomimeticIonChannelGatingRepository


@pytest.mark.asyncio
async def test_biomimetic_ion_channel_gating_repository(db_session):
    repo = BiomimeticIonChannelGatingRepository(db_session)

    study = await repo.create_study(
        name="Study_318_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="biomimetic-ion-channel-gating",
        potassium_over_sodium_selectivity_ratio=142.0,
        single_channel_conductance_pico_siemens=85.0,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 318 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_318_Verification"
    assert getattr(study, "potassium_over_sodium_selectivity_ratio") == 142.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Crown_Ether_Functionalized_Graphene_K_Plus_Selective_Pore",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Crown_Ether_Functionalized_Graphene_K_Plus_Selective_Pore"

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
    assert fetched.name == "Study_318_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
