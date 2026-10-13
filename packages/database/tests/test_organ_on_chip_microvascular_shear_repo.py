"""Tests for Phase 458: Autonomous Organ-on-Chip Multi-Tissue Microvascular Fluid Shear Stress Perfusion Engine Repo."""

import pytest
from database.repositories.organ_on_chip_microvascular_shear_repo import OrganOnChipMicrovascularShearRepository


@pytest.mark.asyncio
async def test_organ_on_chip_microvascular_shear_repository(db_session):
    repo = OrganOnChipMicrovascularShearRepository(db_session)

    study = await repo.create_study(
        name="Study_458_Verification",
        target_specimen="Dual-Channel Microfluidic Blood-Brain Barrier Chip with Pericytes and Endothelial Shear",
        analytical_modality="microvascular-fluid-shear",
        wall_shear_stress_dynes_per_cm2=14.8,
        transendothelial_electrical_resistance_teer_ohm_cm2=1850.0,
        dextran_permeability_coefficient_cm_per_s=1.2e-05,
        endothelial_alignment_angle_std_deg=8.4,
        confidence_score=0.992,
        status="completed",
        summary_report="Phase 458 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_458_Verification"
    assert study.wall_shear_stress_dynes_per_cm2 == 14.8

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Laminar_Shear_Endothelial_Tight_Junction_Integrity",
        profile_category="Primary Step",
        quantitative_value=14.8,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Laminar_Shear_Endothelial_Tight_Junction_Integrity"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="wall_shear_stress_dynes_per_cm2",
        observed_value=14.8,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 14.8

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_458_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
