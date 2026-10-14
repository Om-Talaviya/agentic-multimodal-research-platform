"""Tests for Phase 502: Autonomous Microfluidic Acoustic Sorting & Droplet Single-Exosome Surface Tetraspanin Profiler Repo."""

import pytest
from database.repositories.acoustic_droplet_single_exosome_profiler_repo import AcousticDropletSingleExosomeProfilerRepository


@pytest.mark.asyncio
async def test_acoustic_droplet_single_exosome_profiler_repository(db_session):
    repo = AcousticDropletSingleExosomeProfilerRepository(db_session)

    study = await repo.create_study(
        name="Study_502_Verification",
        target_specimen="Surface Acoustic Wave (SAW) Focused Patient Plasma with CD63/CD81/CD9 Fluorophore Micro-Beads",
        analytical_modality="acoustic-droplet-single-exosome",
        exosome_acoustic_separation_purity_pct=96.8,
        droplet_single_vesicle_encapsulation_lambda=0.28,
        tetraspanin_triplet_colocalization_score=0.915,
        low_abundant_cargo_detection_limit_fM=15.0,
        confidence_score=0.99,
        status="completed",
        summary_report="Phase 502 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_502_Verification"
    assert study.exosome_acoustic_separation_purity_pct == 96.8

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Surface_Acoustic_Wave_Radiation_Force_Focusing",
        profile_category="Primary Step",
        quantitative_value=96.8,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Surface_Acoustic_Wave_Radiation_Force_Focusing"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="exosome_acoustic_separation_purity_pct",
        observed_value=96.8,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 96.8

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_502_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
