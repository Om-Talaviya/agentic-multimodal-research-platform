"""Tests for Phase 519: Autonomous Non-Equilibrium Active Matter Cytoskeletal Topological Defect Self-Propulsion Simulator Repo."""

import pytest
from database.repositories.active_matter_cytoskeletal_nematic_defect_repo import ActiveMatterCytoskeletalNematicDefectRepository


@pytest.mark.asyncio
async def test_active_matter_cytoskeletal_nematic_defect_repository(db_session):
    repo = ActiveMatterCytoskeletalNematicDefectRepository(db_session)

    study = await repo.create_study(
        name="Study_519_Verification",
        target_specimen="Microtubule-Kinesin Active Gel Nematic Liquid Crystal Layer at Oil-Water Interface",
        analytical_modality="active-nematic-matter-dynamics",
        topological_defect_annihilation_rate_s_inv=0.45,
        active_turbulent_vortex_correlation_length_um=18.5,
        plus_half_defect_self_propulsion_velocity_um_per_s=4.8,
        atp_fuel_hydrolysis_energy_dissipation_rate_W_per_m3=12.4,
        confidence_score=0.993,
        status="completed",
        summary_report="Phase 519 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_519_Verification"
    assert study.topological_defect_annihilation_rate_s_inv == 0.45

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Plus_Half_Comet_Shaped_Nematic_Topological_Defect",
        profile_category="Primary Step",
        quantitative_value=0.45,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Plus_Half_Comet_Shaped_Nematic_Topological_Defect"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="topological_defect_annihilation_rate_s_inv",
        observed_value=0.45,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 0.45

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_519_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
