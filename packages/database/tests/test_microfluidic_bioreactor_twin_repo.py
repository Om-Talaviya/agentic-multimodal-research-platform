"""Tests for Phase 384: Autonomous Continuous Flow Microfluidic Bioreactor Nutrient Mixing & Bioprocess Digital Twin Repo."""

import pytest
from database.repositories.microfluidic_bioreactor_twin_repo import MicrofluidicBioreactorTwinRepository


@pytest.mark.asyncio
async def test_microfluidic_bioreactor_twin_repository(db_session):
    repo = MicrofluidicBioreactorTwinRepository(db_session)

    study = await repo.create_study(
        name="Study_384_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="microfluidic-bioreactor-twin",
        volumetric_oxygen_mass_transfer_kla_hr=185.0,
        bioreactor_cell_density_viable_cells_per_ml_million=85.0,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 384 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_384_Verification"
    assert getattr(study, "volumetric_oxygen_mass_transfer_kla_hr") == 185.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Continuous_Perfusion_CHO_Cell_Bioreactor_CFD_Digital_Twin",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Continuous_Perfusion_CHO_Cell_Bioreactor_CFD_Digital_Twin"

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
    assert fetched.name == "Study_384_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
