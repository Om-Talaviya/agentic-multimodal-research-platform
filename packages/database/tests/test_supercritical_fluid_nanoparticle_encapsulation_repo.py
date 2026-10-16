"""Tests for Phase 555: Autonomous Microfluidic High-Pressure Supercritical Fluid Nanoparticle Encapsulation Engine Repo."""

import pytest
from database.repositories.supercritical_fluid_nanoparticle_encapsulation_repo import SupercriticalFluidNanoparticleEncapsulationRepository


@pytest.mark.asyncio
async def test_supercritical_fluid_nanoparticle_encapsulation_repository(db_session):
    repo = SupercriticalFluidNanoparticleEncapsulationRepository(db_session)

    study = await repo.create_study(
        name="Study_555_Verification",
        target_specimen="Supercritical CO2 Rapid Expansion (RESS-SC) of PLGA-PEG Encapsulating Hydrophobic Paclitaxel and Cy5.5 Nanotracers",
        analytical_modality="supercritical-fluid-nanoparticle",
        nanoparticle_mean_hydrodynamic_diameter_nm=68.5,
        encapsulation_efficiency_payload_pct=94.2,
        polydispersity_index_pdi=0.082,
        supercritical_operating_pressure_bar=185.0,
        confidence_score=0.995,
        status="completed",
        summary_report="Phase 555 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_555_Verification"
    assert study.nanoparticle_mean_hydrodynamic_diameter_nm == 68.5

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Uniform_PLGA_Supercritical_Core_Shell_Nanosphere",
        profile_category="Primary Step",
        quantitative_value=68.5,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Uniform_PLGA_Supercritical_Core_Shell_Nanosphere"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="nanoparticle_mean_hydrodynamic_diameter_nm",
        observed_value=68.5,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 68.5

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_555_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
