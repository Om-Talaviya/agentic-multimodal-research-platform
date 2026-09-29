"""Tests for Phase 274: Autonomous Cell-Free TX-TL Synthetic Gene Circuit Kinetic Characterization & Metabolic Flux Optimizer Repo."""

import pytest
from database.repositories.cell_free_txtl_kinetic_optimizer_repo import CellFreeTxtlKineticOptimizerRepository


@pytest.mark.asyncio
async def test_cell_free_txtl_kinetic_optimizer_repository(db_session):
    repo = CellFreeTxtlKineticOptimizerRepository(db_session)

    study = await repo.create_study(
        name="Study_274_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="cell-free-txtl-kinetic-optimizer",
        txtl_protein_synthesis_yield_ug_mL=480.5,
        resource_depletion_half_life_hours=6.8,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 274 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_274_Verification"
    assert getattr(study, "txtl_protein_synthesis_yield_ug_mL") == 480.5

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Cascaded_Incoherent_Feed_Forward_Loop_TXTL_Optimization",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Cascaded_Incoherent_Feed_Forward_Loop_TXTL_Optimization"

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
    assert fetched.name == "Study_274_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
