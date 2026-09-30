"""Tests for Phase 395: Ultra-High Throughput Digital Droplet PCR Copy Number Variation Engine Repo."""

import pytest
from database.repositories.microfluidic_droplet_pcr_repo import MicrofluidicDropletPcrRepository


@pytest.mark.asyncio
async def test_microfluidic_droplet_pcr_repository(db_session):
    repo = MicrofluidicDropletPcrRepository(db_session)

    study = await repo.create_study(
        name="Study_395_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="microfluidic-droplet-pcr",
        droplet_generation_monodispersity_cv_pct=1.8,
        cnv_absolute_quantification_precision_pct=99.6,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 395 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_395_Verification"
    assert getattr(study, "droplet_generation_monodispersity_cv_pct") == 1.8

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="HER2_ERBB2_Gene_Amplification_Copy_Number_Partition_Array",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "HER2_ERBB2_Gene_Amplification_Copy_Number_Partition_Array"

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
    assert fetched.name == "Study_395_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
