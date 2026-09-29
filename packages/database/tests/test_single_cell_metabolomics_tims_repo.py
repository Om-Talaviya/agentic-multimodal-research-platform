"""Tests for Phase 292: Autonomous Single-Cell Metabolomics Trapped Ion Mobility Spectrometry (TIMS) Flux Deconvolution Engine Repo."""

import pytest
from database.repositories.single_cell_metabolomics_tims_repo import SingleCellMetabolomicsTimsRepository


@pytest.mark.asyncio
async def test_single_cell_metabolomics_tims_repository(db_session):
    repo = SingleCellMetabolomicsTimsRepository(db_session)

    study = await repo.create_study(
        name="Study_292_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="single-cell-metabolomics-tims",
        single_cell_metabolite_coverage_depth=420.0,
        cellular_atp_adp_energy_charge_ratio=4.6,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 292 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_292_Verification"
    assert getattr(study, "single_cell_metabolite_coverage_depth") == 420.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Glioblastoma_Single_Cell_Glycolytic_Flux_Map",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Glioblastoma_Single_Cell_Glycolytic_Flux_Map"

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
    assert fetched.name == "Study_292_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
