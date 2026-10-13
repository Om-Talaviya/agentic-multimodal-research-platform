"""Tests for Phase 465: Autonomous Microfluidic Acoustic Tweezers Multicellular Spheroid Patterning & Cytoskeletal Stress Engine Repo."""

import pytest
from database.repositories.acoustic_tweezers_spheroid_patterning_repo import AcousticTweezersSpheroidPatterningRepository


@pytest.mark.asyncio
async def test_acoustic_tweezers_spheroid_patterning_repository(db_session):
    repo = AcousticTweezersSpheroidPatterningRepository(db_session)

    study = await repo.create_study(
        name="Study_465_Verification",
        target_specimen="3D MCF-7 Breast Tumor Spheroid Array patterned in 2.5 MHz Standing Bulk Acoustic Wave Resonator",
        analytical_modality="acoustic-spheroid-patterning",
        acoustic_radiation_force_pN=42.5,
        spheroid_diameter_uniformity_cv=0.048,
        cytoskeletal_f_actin_alignment_index=0.885,
        acoustic_trapping_node_stability=0.992,
        confidence_score=0.991,
        status="completed",
        summary_report="Phase 465 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_465_Verification"
    assert study.acoustic_radiation_force_pN == 42.5

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Standing_Acoustic_Pressure_Node_Aggregation",
        profile_category="Primary Step",
        quantitative_value=42.5,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Standing_Acoustic_Pressure_Node_Aggregation"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="acoustic_radiation_force_pN",
        observed_value=42.5,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 42.5

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_465_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
