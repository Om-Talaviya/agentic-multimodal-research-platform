"""Tests for Phase 341: Autonomous In Silico Organoid Microfluidic Shear Stress & Nutrient Diffusion Twin Repo."""

import pytest
from database.repositories.organoid_microfluidic_shear_twin_repo import OrganoidMicrofluidicShearTwinRepository


@pytest.mark.asyncio
async def test_organoid_microfluidic_shear_twin_repository(db_session):
    repo = OrganoidMicrofluidicShearTwinRepository(db_session)

    study = await repo.create_study(
        name="Study_341_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="organoid-microfluidic-twin",
        physiologic_wall_shear_stress_dynes_cm2=15.4,
        core_hypoxia_volume_fraction_pct=1.85,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 341 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_341_Verification"
    assert getattr(study, "physiologic_wall_shear_stress_dynes_cm2") == 15.4

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Blood_Brain_Barrier_Chip_Endothelial_Shear_Permeability_Twin",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Blood_Brain_Barrier_Chip_Endothelial_Shear_Permeability_Twin"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="Sensitivity & Recovery Rate",
        observed_value=0.984,
        z_score=2.85,
        p_value=0.00012,
    )
    assert trace.id is not None
    assert trace.observed_value == 0.984

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_341_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
