"""Tests for Phase 464: Autonomous Synthetic Symbiotic Consortia Metabolic Division-of-Labor Population Dynamics Simulator Repo."""

import pytest
from database.repositories.symbiotic_consortia_division_of_labor_repo import SymbioticConsortiaDivisionOfLaborRepository


@pytest.mark.asyncio
async def test_symbiotic_consortia_division_of_labor_repository(db_session):
    repo = SymbioticConsortiaDivisionOfLaborRepository(db_session)

    study = await repo.create_study(
        name="Study_464_Verification",
        target_specimen="Engineered E. coli and S. cerevisiae Cross-Feeding Co-Culture in Chemostat Bioreactor",
        analytical_modality="symbiotic-metabolic-labor-dynamics",
        chemostat_steady_state_biomass_ratio=1.15,
        cross_feeding_metabolite_exchange_flux_mmol_g_hr=6.85,
        population_coexistence_lyapunov_exponent=-0.42,
        resource_utilization_synergy_factor=1.85,
        confidence_score=0.99,
        status="completed",
        summary_report="Phase 464 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_464_Verification"
    assert study.chemostat_steady_state_biomass_ratio == 1.15

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Cross_Feeding_Acetate_Glucose_Exchange_Flux",
        profile_category="Primary Step",
        quantitative_value=1.15,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Cross_Feeding_Acetate_Glucose_Exchange_Flux"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="chemostat_steady_state_biomass_ratio",
        observed_value=1.15,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 1.15

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_464_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
