"""Tests for Phase 510: Autonomous Vascularized Cerebral Organoid Lumen Shear Stress & Perfusion Simulator Repo."""

import pytest
from database.repositories.organoid_vascular_perfusion_endothelial_shear_repo import OrganoidVascularPerfusionEndothelialShearRepository


@pytest.mark.asyncio
async def test_organoid_vascular_perfusion_endothelial_shear_repository(db_session):
    repo = OrganoidVascularPerfusionEndothelialShearRepository(db_session)

    study = await repo.create_study(
        name="Study_510_Verification",
        target_specimen="3D Bioprinted Endothelialized Hydrogel Microchannel Lattice Interfaced with Cortical Brain Organoids",
        analytical_modality="organoid-microvascular-perfusion",
        microvascular_lumen_wall_shear_stress_pa=1.45,
        interstitial_oxygen_partial_pressure_mmHg=38.5,
        core_necrotic_zone_reduction_ratio=0.945,
        tight_junction_claudin5_teer_ohm_cm2=1850.0,
        confidence_score=0.995,
        status="completed",
        summary_report="Phase 510 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_510_Verification"
    assert study.microvascular_lumen_wall_shear_stress_pa == 1.45

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Capillary_Endothelial_Lumen_Oxygenation_Flux",
        profile_category="Primary Step",
        quantitative_value=1.45,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Capillary_Endothelial_Lumen_Oxygenation_Flux"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="microvascular_lumen_wall_shear_stress_pa",
        observed_value=1.45,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 1.45

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_510_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
