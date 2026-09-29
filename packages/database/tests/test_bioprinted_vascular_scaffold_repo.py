"""Tests for Phase 366: Autonomous 3D Bioprinted Vascularized Tissue Scaffold Fluid Shear & Endothelial Sprouting Simulator Repo."""

import pytest
from database.repositories.bioprinted_vascular_scaffold_repo import BioprintedVascularScaffoldRepository


@pytest.mark.asyncio
async def test_bioprinted_vascular_scaffold_repository(db_session):
    repo = BioprintedVascularScaffoldRepository(db_session)

    study = await repo.create_study(
        name="Study_366_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="bioprinted-vascular-scaffold",
        capillary_network_perfusion_flow_rate_ul_min=125.0,
        endothelial_lumen_patency_fraction_pct=98.2,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 366 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_366_Verification"
    assert getattr(study, "capillary_network_perfusion_flow_rate_ul_min") == 125.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Hepatic_Lobule_Perfused_Microvascular_GelMA_Scaffold",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Hepatic_Lobule_Perfused_Microvascular_GelMA_Scaffold"

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
    assert fetched.name == "Study_366_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
