"""Tests for Phase 530: Autonomous Bacterial Outer Membrane Vesicle (OMV) Biogenesis & Cargo Sorting Predictor Repo."""

import pytest
from database.repositories.bacterial_outer_membrane_vesicle_packaging_repo import BacterialOuterMembraneVesiclePackagingRepository


@pytest.mark.asyncio
async def test_bacterial_outer_membrane_vesicle_packaging_repository(db_session):
    repo = BacterialOuterMembraneVesiclePackagingRepository(db_session)

    study = await repo.create_study(
        name="Study_530_Verification",
        target_specimen="Hyper-Vesiculating Engineered Pseudomonas aeruginosa Strain PAO1 Membrane Fractions",
        analytical_modality="omv-biogenesis-cargo-sorting",
        vesiculation_rate_omv_per_cell_hr=145.0,
        cargo_virulence_factor_enrichment_ratio=8.4,
        vesicle_average_hydrodynamic_diameter_nm=82.5,
        lps_phospholipid_asymmetry_index=0.94,
        confidence_score=0.992,
        status="completed",
        summary_report="Phase 530 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_530_Verification"
    assert study.vesiculation_rate_omv_per_cell_hr == 145.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Outer_Membrane_Budding_Curvature_Neck",
        profile_category="Primary Step",
        quantitative_value=145.0,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Outer_Membrane_Budding_Curvature_Neck"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="vesiculation_rate_omv_per_cell_hr",
        observed_value=145.0,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 145.0

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_530_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
