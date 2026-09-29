"""Tests for Phase 333: Autonomous Chemically-Induced Proximity & Degron Ligand Multi-Body Assembly Engine Repo."""

import pytest
from database.repositories.chemical_proximity_degron_repo import ChemicalProximityDegronRepository


@pytest.mark.asyncio
async def test_chemical_proximity_degron_repository(db_session):
    repo = ChemicalProximityDegronRepository(db_session)

    study = await repo.create_study(
        name="Study_333_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="chemical-proximity-degron",
        ternary_complex_cooperativity_factor_alpha=18.6,
        target_ubiquitination_half_life_min=14.2,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 333 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_333_Verification"
    assert getattr(study, "ternary_complex_cooperativity_factor_alpha") == 18.6

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="VHL_E3_Ligase_BRD4_Proteolysis_Targeting_Chimera_Complex",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "VHL_E3_Ligase_BRD4_Proteolysis_Targeting_Chimera_Complex"

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
    assert fetched.name == "Study_333_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
