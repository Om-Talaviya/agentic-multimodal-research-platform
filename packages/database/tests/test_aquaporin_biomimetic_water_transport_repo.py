"""Tests for Phase 491: Autonomous Biomimetic Synthetic Membrane Water Aquaporin Channel Transport Forecaster Repo."""

import pytest
from database.repositories.aquaporin_biomimetic_water_transport_repo import AquaporinBiomimeticWaterTransportRepository


@pytest.mark.asyncio
async def test_aquaporin_biomimetic_water_transport_repository(db_session):
    repo = AquaporinBiomimeticWaterTransportRepository(db_session)

    study = await repo.create_study(
        name="Study_491_Verification",
        target_specimen="Polymer-Inorganic Biomimetic Aquaporin-Z Nanocomposite Membrane with Forward Osmosis Crossflow",
        analytical_modality="aquaporin-biomimetic-transport",
        water_permeability_flux_lmh_bar=48.5,
        nacl_solute_rejection_percentage=99.4,
        aquaporin_channel_incorporation_density_per_um2=12500.0,
        single_pore_osmotic_permeability_pf_cm3_per_s=4.2e-14,
        confidence_score=0.992,
        status="completed",
        summary_report="Phase 491 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_491_Verification"
    assert study.water_permeability_flux_lmh_bar == 48.5

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Single_File_Water_Molecule_Hop_Through_AqPZ_Pore",
        profile_category="Primary Step",
        quantitative_value=48.5,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Single_File_Water_Molecule_Hop_Through_AqPZ_Pore"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="water_permeability_flux_lmh_bar",
        observed_value=48.5,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 48.5

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_491_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
