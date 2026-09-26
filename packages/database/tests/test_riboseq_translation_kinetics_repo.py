"""Tests for Phase 196: Ribosome Profiling & Translation Efficiency Deconvolution Engine Repo."""

import pytest
from database.repositories.riboseq_translation_kinetics_repo import RiboSeqTranslationKineticsRepository


@pytest.mark.asyncio
async def test_riboseq_translation_kinetics_repository(db_session):
    repo = RiboSeqTranslationKineticsRepository(db_session)

    study = await repo.create_study(
        name="Study_196_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="Ribo-seq Translation Kinetics",
        mean_translation_efficiency_log2=2.85,
        ribosome_dwell_time_ms=48.2,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 196 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_196_Verification"
    assert getattr(study, "mean_translation_efficiency_log2") == 2.85

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="High-Efficiency CDS Footprint Cluster [Myc Oncoprotein]",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "High-Efficiency CDS Footprint Cluster [Myc Oncoprotein]"

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
    assert fetched.name == "Study_196_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
