"""Tests for Phase 305: Autonomous In-Silico Nanopore Adaptive Real-Time Selective Sequencing ReadUntil Bio-Threat Sentinel Repo."""

import pytest
from database.repositories.nanopore_readuntil_threat_sentinel_repo import NanoporeReaduntilThreatSentinelRepository


@pytest.mark.asyncio
async def test_nanopore_readuntil_threat_sentinel_repository(db_session):
    repo = NanoporeReaduntilThreatSentinelRepository(db_session)

    study = await repo.create_study(
        name="Study_305_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="nanopore-readuntil-threat-sentinel",
        target_pathogen_enrichment_fold=18.5,
        real_time_classification_latency_ms=220.0,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 305 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_305_Verification"
    assert getattr(study, "target_pathogen_enrichment_fold") == 18.5

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Respiratory_Metagenomic_Viral_Pathogen_Enrichment",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Respiratory_Metagenomic_Viral_Pathogen_Enrichment"

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
    assert fetched.name == "Study_305_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
