"""Tests for Phase 500: Autonomous Bioelectronic Living Biomaterial Microbial Electron Transport Network Modeler Repo."""

import pytest
from database.repositories.bioelectronic_living_materials_network_repo import BioelectronicLivingMaterialsNetworkRepository


@pytest.mark.asyncio
async def test_bioelectronic_living_materials_network_repository(db_session):
    repo = BioelectronicLivingMaterialsNetworkRepository(db_session)

    study = await repo.create_study(
        name="Study_500_Verification",
        target_specimen="Geobacter sulfurreducens Engineered Electrically Conductive Cytochrome Pili Hydrogel Matrix",
        analytical_modality="bioelectronic-living-materials",
        matrix_electrical_conductivity_S_per_cm=0.85,
        redox_cytochrome_hopping_rate_s_inv=420000.0,
        current_density_production_mA_per_cm2=18.5,
        longitudinal_charge_transfer_efficiency=0.965,
        confidence_score=0.991,
        status="completed",
        summary_report="Phase 500 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_500_Verification"
    assert study.matrix_electrical_conductivity_S_per_cm == 0.85

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="OmcS_Cytochrome_Filament_Electron_Delocalization",
        profile_category="Primary Step",
        quantitative_value=0.85,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "OmcS_Cytochrome_Filament_Electron_Delocalization"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="matrix_electrical_conductivity_S_per_cm",
        observed_value=0.85,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 0.85

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_500_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
