"""Tests for Phase 302: Autonomous In-Silico Whole-Organ Vascular Micro-Perfusion & Dynamic Oxygen Gradient Hemodynamics Simulator Repo."""

import pytest
from database.repositories.whole_organ_vascular_perfusion_repo import WholeOrganVascularPerfusionRepository


@pytest.mark.asyncio
async def test_whole_organ_vascular_perfusion_repository(db_session):
    repo = WholeOrganVascularPerfusionRepository(db_session)

    study = await repo.create_study(
        name="Study_302_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="whole-organ-vascular-perfusion",
        microvascular_perfusion_flow_rate_mL_min=125.0,
        tissue_hypoxia_gradient_dissipation_r2=0.94,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 302 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_302_Verification"
    assert getattr(study, "microvascular_perfusion_flow_rate_mL_min") == 125.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Hepatic_Lobule_Zonation_Oxygen_Gradient_Perfusion",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Hepatic_Lobule_Zonation_Oxygen_Gradient_Perfusion"

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
    assert fetched.name == "Study_302_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
