"""Tests for Phase 352: Autonomous Multiplexed Ion Beam Imaging (MIBI-TOF) Deep Proteomic Spatial TME Deconvolver Repo."""

import pytest
from database.repositories.mibi_tof_spatial_proteomics_repo import MibiTofSpatialProteomicsRepository


@pytest.mark.asyncio
async def test_mibi_tof_spatial_proteomics_repository(db_session):
    repo = MibiTofSpatialProteomicsRepository(db_session)

    study = await repo.create_study(
        name="Study_352_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="mibi-tof-spatial-proteomics",
        lateral_spatial_resolution_nanometers=260.0,
        isotopic_ion_channel_signal_to_noise_ratio=84.5,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 352 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_352_Verification"
    assert getattr(study, "lateral_spatial_resolution_nanometers") == 260.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Triple_Negative_Breast_Cancer_40_Channel_MIBI_Tissue_Grid",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Triple_Negative_Breast_Cancer_40_Channel_MIBI_Tissue_Grid"

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
    assert fetched.name == "Study_352_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
