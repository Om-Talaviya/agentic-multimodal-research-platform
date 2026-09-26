"""Tests for Phase 223: Autonomous Heavy-Chain Nanobody (VHH) Paratope Deep Mutational Scanning (DMS) & Conformational Thermal Stability Engine Repo."""

import pytest
from database.repositories.nanobody_paratope_deep_mutational_repo import NanobodyParatopeDeepMutationalRepository


@pytest.mark.asyncio
async def test_nanobody_paratope_deep_mutational_repository(db_session):
    repo = NanobodyParatopeDeepMutationalRepository(db_session)

    study = await repo.create_study(
        name="Study_223_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="nanobody-paratope-deep-mutational",
        thermal_melting_shift_celsius=8.5,
        affinity_kd_enrichment_fold=14.2,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 223 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_223_Verification"
    assert getattr(study, "thermal_melting_shift_celsius") == 8.5

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="VHH_AntiEGFR_CDR3_DeepMutational_Scan",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "VHH_AntiEGFR_CDR3_DeepMutational_Scan"

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
    assert fetched.name == "Study_223_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
