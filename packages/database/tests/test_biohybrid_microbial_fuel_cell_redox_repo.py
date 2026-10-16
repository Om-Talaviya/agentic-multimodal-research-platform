"""Tests for Phase 559: Autonomous Biohybrid Microbial Fuel Cell Extracellular Electron Shuttle Redox Kinetics Simulator Repo."""

import pytest
from database.repositories.biohybrid_microbial_fuel_cell_redox_repo import BiohybridMicrobialFuelCellRedoxRepository


@pytest.mark.asyncio
async def test_biohybrid_microbial_fuel_cell_redox_repository(db_session):
    repo = BiohybridMicrobialFuelCellRedoxRepository(db_session)

    study = await repo.create_study(
        name="Study_559_Verification",
        target_specimen="Shewanella oneidensis MR-1 living Biofilm grown on 3D Carbon Nanotube Anode with Riboflavin Redox Mediators",
        analytical_modality="biohybrid-microbial-fuel-cell",
        anodic_current_density_ma_cm2=14.8,
        extracellular_electron_transfer_rate_per_sec=820.0,
        cytochrome_mtrc_reduction_potential_mv=-140.0,
        fuel_cell_maximum_power_density_mw_m2=2450.0,
        confidence_score=0.994,
        status="completed",
        summary_report="Phase 559 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_559_Verification"
    assert study.anodic_current_density_ma_cm2 == 14.8

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Outer_Membrane_MtrCAB_Flavin_Electron_Conduit_Matrix",
        profile_category="Primary Step",
        quantitative_value=14.8,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Outer_Membrane_MtrCAB_Flavin_Electron_Conduit_Matrix"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="anodic_current_density_ma_cm2",
        observed_value=14.8,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 14.8

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_559_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
