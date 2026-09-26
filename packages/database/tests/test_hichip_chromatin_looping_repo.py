"""Tests for Phase 200: Epigenomic Hi-ChIP & Enhancer-Promoter Chromatin Looping Engine Repo."""

import pytest
from database.repositories.hichip_chromatin_looping_repo import HiChIPChromatinLoopingRepository


@pytest.mark.asyncio
async def test_hichip_chromatin_looping_repository(db_session):
    repo = HiChIPChromatinLoopingRepository(db_session)

    study = await repo.create_study(
        name="Study_200_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="Hi-ChIP Chromatin Looping",
        loop_contact_enrichment_score=8.74,
        enhancer_promoter_interaction_strength=0.945,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 200 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_200_Verification"
    assert getattr(study, "loop_contact_enrichment_score") == 8.74

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="H3K27ac-Anchored Super-Enhancer Loop [MYC Locus]",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "H3K27ac-Anchored Super-Enhancer Loop [MYC Locus]"

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
    assert fetched.name == "Study_200_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
