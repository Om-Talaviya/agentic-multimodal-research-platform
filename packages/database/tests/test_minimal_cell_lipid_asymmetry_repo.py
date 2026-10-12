"""Tests for Phase 423: Autonomous Synthetic Minimal Cell Membrane Lipid Bilayer Asymmetry & Vesicle Budding Engine Repo."""

import pytest
from database.repositories.minimal_cell_lipid_asymmetry_repo import MinimalCellLipidAsymmetryRepository


@pytest.mark.asyncio
async def test_minimal_cell_lipid_asymmetry_repository(db_session):
    repo = MinimalCellLipidAsymmetryRepository(db_session)

    study = await repo.create_study(
        name="Study_423_Verification",
        target_specimen="Synthetic Giant Unilamellar Vesicle (GUV) with Flippase ABCB4",
        analytical_modality="minimal-cell-lipid",
        bilayer_asymmetry_index=0.884,
        membrane_bending_rigidity_kbt=18.2,
        vesicle_budding_rate_um_per_min=0.35,
        inner_leaflet_phosphatidylserine_ratio=0.912,
        confidence_score=0.986,
        status="completed",
        summary_report="Phase 423 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_423_Verification"
    assert study.bilayer_asymmetry_index == 0.884

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Asymmetric_Leaflet_Spontaneous_Curvature",
        profile_category="Primary Step",
        quantitative_value=0.884,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Asymmetric_Leaflet_Spontaneous_Curvature"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="bilayer_asymmetry_index",
        observed_value=0.884,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 0.884

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_423_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
