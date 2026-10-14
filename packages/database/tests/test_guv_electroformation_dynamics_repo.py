"""Tests for Phase 480: Autonomous Synthetic Protocellular Giant Unilamellar Vesicle (GUV) Electroformation Simulator Repo."""

import pytest
from database.repositories.guv_electroformation_dynamics_repo import GuvElectroformationDynamicsRepository


@pytest.mark.asyncio
async def test_guv_electroformation_dynamics_repository(db_session):
    repo = GuvElectroformationDynamicsRepository(db_session)

    study = await repo.create_study(
        name="Study_480_Verification",
        target_specimen="Indium Tin Oxide (ITO) Microelectrode Chamber with POPC/Cholesterol Bilayer Hydration",
        analytical_modality="guv-electroformation-dynamics",
        guv_mean_diameter_yield_um=28.5,
        bilayer_bending_rigidity_kbT=22.4,
        electric_field_interfacial_shear_V_per_m=1200.0,
        unilamellarity_monodispersity_cv=0.065,
        confidence_score=0.989,
        status="completed",
        summary_report="Phase 480 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_480_Verification"
    assert study.guv_mean_diameter_yield_um == 28.5

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="AC_Electric_Field_Lipid_Budding_Detachment",
        profile_category="Primary Step",
        quantitative_value=28.5,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "AC_Electric_Field_Lipid_Budding_Detachment"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="guv_mean_diameter_yield_um",
        observed_value=28.5,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 28.5

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_480_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
