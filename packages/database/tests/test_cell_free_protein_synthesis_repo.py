"""Tests for Phase 387: Autonomous Cell-Free Protein Synthesis (CFPS) Metabolic Energy Regeneration Engine Repo."""

import pytest
from database.repositories.cell_free_protein_synthesis_repo import CellFreeProteinSynthesisRepository


@pytest.mark.asyncio
async def test_cell_free_protein_synthesis_repository(db_session):
    repo = CellFreeProteinSynthesisRepository(db_session)

    study = await repo.create_study(
        name="Study_387_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="cell-free-protein-synthesis",
        cell_free_protein_yield_mg_per_ml=2.85,
        atp_energy_regeneration_flux_umol_min=64.0,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 387 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_387_Verification"
    assert getattr(study, "cell_free_protein_yield_mg_per_ml") == 2.85

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Lyophilized_E_coli_CFPS_Therapeutic_On_Demand_Workcell",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Lyophilized_E_coli_CFPS_Therapeutic_On_Demand_Workcell"

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
    assert fetched.name == "Study_387_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
