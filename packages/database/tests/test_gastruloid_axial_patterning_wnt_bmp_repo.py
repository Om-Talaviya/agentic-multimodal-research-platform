"""Tests for Phase 496: Autonomous Synthetic Organogenesis Gastruloid Axial Patterning & Wnt-BMP Morphogenetic Polarization Engine Repo."""

import pytest
from database.repositories.gastruloid_axial_patterning_wnt_bmp_repo import GastruloidAxialPatterningWntBmpRepository


@pytest.mark.asyncio
async def test_gastruloid_axial_patterning_wnt_bmp_repository(db_session):
    repo = GastruloidAxialPatterningWntBmpRepository(db_session)

    study = await repo.create_study(
        name="Study_496_Verification",
        target_specimen="3D Aggregated Human Embryonic Stem Cell Gastruloids under Chir99021 Pulse Induction",
        analytical_modality="gastruloid-axial-patterning",
        anteroposterior_elongation_aspect_ratio=3.65,
        bra_t_posterior_polarization_fraction=0.925,
        somite_like_segmentation_stripe_count=8.0,
        morphogenetic_symmetry_breaking_time_hours=48.0,
        confidence_score=0.995,
        status="completed",
        summary_report="Phase 496 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_496_Verification"
    assert study.anteroposterior_elongation_aspect_ratio == 3.65

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Wnt_beta_Catenin_Posterior_Axis_Organizer_Hub",
        profile_category="Primary Step",
        quantitative_value=3.65,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Wnt_beta_Catenin_Posterior_Axis_Organizer_Hub"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="anteroposterior_elongation_aspect_ratio",
        observed_value=3.65,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 3.65

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_496_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
