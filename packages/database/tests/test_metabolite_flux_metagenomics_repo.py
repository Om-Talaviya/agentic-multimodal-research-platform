"""Tests for Phase 225: Autonomous Metagenomic Metabolic Flux & Gut-Liver Axis Co-Metabolism Simulator Engine Repo."""

import pytest
from database.repositories.metabolite_flux_metagenomics_repo import MetaboliteFluxMetagenomicsRepository


@pytest.mark.asyncio
async def test_metabolite_flux_metagenomics_repository(db_session):
    repo = MetaboliteFluxMetagenomicsRepository(db_session)

    study = await repo.create_study(
        name="Study_225_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="metabolite-flux-metagenomics",
        scfa_butyrate_production_mmol_gDW_h=14.8,
        microbiome_host_flux_coupling_index=0.92,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 225 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_225_Verification"
    assert getattr(study, "scfa_butyrate_production_mmol_gDW_h") == 14.8

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Akkermansia_Muciniphila_Mucin_Turnover_Flux",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Akkermansia_Muciniphila_Mucin_Turnover_Flux"

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
    assert fetched.name == "Study_225_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
