"""Tests for Phase 310: Autonomous Next-Gen Prime Editing (PE6/PE7) Dual-Engineered pegRNA Design & Transversion Optimization Engine Repo."""

import pytest
from database.repositories.prime_editing_pe6_peg_rna_evaluator_repo import PrimeEditingPe6PegRnaEvaluatorRepository


@pytest.mark.asyncio
async def test_prime_editing_pe6_peg_rna_evaluator_repository(db_session):
    repo = PrimeEditingPe6PegRnaEvaluatorRepository(db_session)

    study = await repo.create_study(
        name="Study_310_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="prime-editing-pe6-peg-rna",
        prime_editing_efficiency_pct=89.6,
        bystander_indel_frequency_pct=0.12,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 310 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_310_Verification"
    assert getattr(study, "prime_editing_efficiency_pct") == 89.6

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Cystic_Fibrosis_CFTR_DeltaF508_PE6_Repair_Construct",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Cystic_Fibrosis_CFTR_DeltaF508_PE6_Repair_Construct"

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
    assert fetched.name == "Study_310_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
