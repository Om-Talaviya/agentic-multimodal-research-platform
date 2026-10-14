"""Tests for Phase 501: Autonomous CRISPR-Associated Transposase (CAST) Targeted Large Genomic Cargo Integrator Repo."""

import pytest
from database.repositories.cast_transposase_genomic_integration_repo import CastTransposaseGenomicIntegrationRepository


@pytest.mark.asyncio
async def test_cast_transposase_genomic_integration_repository(db_session):
    repo = CastTransposaseGenomicIntegrationRepository(db_session)

    study = await repo.create_study(
        name="Study_501_Verification",
        target_specimen="Type V-K CRISPR-Cas12k / TnsA-TnsB-TnsC Transposase Complex with 10kb Cargo Plasmid in Human Cells",
        analytical_modality="cast-transposase-integration",
        targeted_insertion_efficiency_pct=68.5,
        on_target_integration_accuracy_pct=99.2,
        cargo_payload_size_capacity_kb=10.0,
        indel_free_junction_preservation_ratio=0.985,
        confidence_score=0.994,
        status="completed",
        summary_report="Phase 501 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_501_Verification"
    assert study.targeted_insertion_efficiency_pct == 68.5

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Cas12k_Guided_TnsB_Transposon_End_Joining",
        profile_category="Primary Step",
        quantitative_value=68.5,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Cas12k_Guided_TnsB_Transposon_End_Joining"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="targeted_insertion_efficiency_pct",
        observed_value=68.5,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 68.5

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_501_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
