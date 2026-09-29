"""Tests for Phase 356: Autonomous High-Throughput Droplet Microfluidic Single-Cell Antibody Screening Sorter Repo."""

import pytest
from database.repositories.droplet_microfluidic_antibody_repo import DropletMicrofluidicAntibodyRepository


@pytest.mark.asyncio
async def test_droplet_microfluidic_antibody_repository(db_session):
    repo = DropletMicrofluidicAntibodyRepository(db_session)

    study = await repo.create_study(
        name="Study_356_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="droplet-microfluidic-antibody",
        droplet_sorting_throughput_droplets_per_sec=10000.0,
        single_cell_encapsulation_monodispersity_pct=99.4,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 356 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_356_Verification"
    assert getattr(study, "droplet_sorting_throughput_droplets_per_sec") == 10000.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Ultra_High_Throughput_10kHz_FADS_B_Cell_Sorting_Channel",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Ultra_High_Throughput_10kHz_FADS_B_Cell_Sorting_Channel"

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
    assert fetched.name == "Study_356_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
