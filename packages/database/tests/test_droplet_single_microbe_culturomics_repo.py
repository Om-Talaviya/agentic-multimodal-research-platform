"""Tests for Phase 320: Autonomous Ultra-High-Throughput Droplet Microfluidic Unculturable Microbe Single-Cell Culturomics Screener Repo."""

import pytest
from database.repositories.droplet_single_microbe_culturomics_repo import DropletSingleMicrobeCulturomicsRepository


@pytest.mark.asyncio
async def test_droplet_single_microbe_culturomics_repository(db_session):
    repo = DropletSingleMicrobeCulturomicsRepository(db_session)

    study = await repo.create_study(
        name="Study_320_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="droplet-single-microbe-culturomics",
        droplet_screening_throughput_droplets_per_sec=2500.0,
        novel_uncultivated_species_recovery_rate_pct=74.5,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 320 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_320_Verification"
    assert getattr(study, "droplet_screening_throughput_droplets_per_sec") == 2500.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Deep_Sea_Hydrothermal_Vent_Novel_Antimicrobial_Droplet_Screen",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Deep_Sea_Hydrothermal_Vent_Novel_Antimicrobial_Droplet_Screen"

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
    assert fetched.name == "Study_320_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
