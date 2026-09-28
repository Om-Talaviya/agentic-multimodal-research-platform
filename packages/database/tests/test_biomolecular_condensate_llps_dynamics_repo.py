"""Tests for Phase 258: Autonomous Liquid-Liquid Phase Separation (LLPS) Biomolecular Condensate Multivalent Driving Force Engine Repo."""

import pytest
from database.repositories.biomolecular_condensate_llps_dynamics_repo import BiomolecularCondensateLlpsDynamicsRepository


@pytest.mark.asyncio
async def test_biomolecular_condensate_llps_dynamics_repository(db_session):
    repo = BiomolecularCondensateLlpsDynamicsRepository(db_session)

    study = await repo.create_study(
        name="Study_258_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="biomolecular-condensate-llps-dynamics",
        critical_saturation_concentration_csat_uM=4.2,
        flory_huggins_interaction_chi_parameter=0.85,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 258 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_258_Verification"
    assert getattr(study, "critical_saturation_concentration_csat_uM") == 4.2

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="FUS_Low_Complexity_Domain_Liquid_Droplet_Simulation",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "FUS_Low_Complexity_Domain_Liquid_Droplet_Simulation"

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
    assert fetched.name == "Study_258_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
