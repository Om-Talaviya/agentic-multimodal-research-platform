"""Tests for Phase 520: Autonomous In-Situ Liquid-Cell Transmission Electron Microscopy Protein Nucleation Real-Time Tracker Repo."""

import pytest
from database.repositories.liquid_cell_tem_protein_crystallization_repo import LiquidCellTemProteinCrystallizationRepository


@pytest.mark.asyncio
async def test_liquid_cell_tem_protein_crystallization_repository(db_session):
    repo = LiquidCellTemProteinCrystallizationRepository(db_session)

    study = await repo.create_study(
        name="Study_520_Verification",
        target_specimen="Silicon Nitride Microchip Graphene Liquid Cell with Supersaturated Hen Egg-White Lysozyme Solution",
        analytical_modality="liquid-cell-tem-crystallization",
        critical_nucleus_radius_nm=2.4,
        non_classical_pre_nucleation_cluster_density_per_um3=1250.0,
        crystal_facet_growth_rate_nm_per_min=1.85,
        electron_beam_dose_induced_radiolysis_damage_threshold_e_per_angstrom2=2.5,
        confidence_score=0.994,
        status="completed",
        summary_report="Phase 520 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_520_Verification"
    assert study.critical_nucleus_radius_nm == 2.4

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Sub_Nanometer_Pre_Nucleation_Dense_Liquid_Precursor",
        profile_category="Primary Step",
        quantitative_value=2.4,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Sub_Nanometer_Pre_Nucleation_Dense_Liquid_Precursor"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="critical_nucleus_radius_nm",
        observed_value=2.4,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 2.4

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_520_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
