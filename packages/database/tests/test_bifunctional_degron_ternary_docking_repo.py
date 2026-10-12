"""Tests for Phase 430: Autonomous Targeted Protein Degradation Bifunctional Degron Heterobifunctional Ternary Interface Docking Forecaster Repo."""

import pytest
from database.repositories.bifunctional_degron_ternary_docking_repo import BifunctionalDegronTernaryDockingRepository


@pytest.mark.asyncio
async def test_bifunctional_degron_ternary_docking_repository(db_session):
    repo = BifunctionalDegronTernaryDockingRepository(db_session)

    study = await repo.create_study(
        name="Study_430_Verification",
        target_specimen="VHL-E3 Ligase, Linker, and Target Oncogenic Kinase Complex",
        analytical_modality="bifunctional-degron-docking",
        ternary_complex_cooperativity_alpha=3.42,
        buried_solvent_accessible_surface_angstrom2=1140.0,
        ubiquitination_zone_distance_angstrom=12.8,
        hook_effect_concentration_uM=2.5,
        confidence_score=0.988,
        status="completed",
        summary_report="Phase 430 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_430_Verification"
    assert study.ternary_complex_cooperativity_alpha == 3.42

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="E3_Target_Induced_Protein_Protein_Interface",
        profile_category="Primary Step",
        quantitative_value=3.42,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "E3_Target_Induced_Protein_Protein_Interface"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="ternary_complex_cooperativity_alpha",
        observed_value=3.42,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 3.42

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_430_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
