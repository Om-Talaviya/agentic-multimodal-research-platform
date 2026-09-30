"""Tests for Phase 385: Autonomous Deep Generative Peptide-HLA-DP/DQ Class II Immunogenicity Predictor Repo."""

import pytest
from database.repositories.peptide_hla_dp_dq_predictor_repo import PeptideHlaDpDqPredictorRepository


@pytest.mark.asyncio
async def test_peptide_hla_dp_dq_predictor_repository(db_session):
    repo = PeptideHlaDpDqPredictorRepository(db_session)

    study = await repo.create_study(
        name="Study_385_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="peptide-hla-dp-dq-predictor",
        class2_pmhc_binding_affinity_auroc=0.962,
        core_register_alignment_accuracy_pct=97.5,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 385 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_385_Verification"
    assert getattr(study, "class2_pmhc_binding_affinity_auroc") == 0.962

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Celiac_Disease_HLA_DQ2_5_Gluten_Deamidated_Epitope_Model",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Celiac_Disease_HLA_DQ2_5_Gluten_Deamidated_Epitope_Model"

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
    assert fetched.name == "Study_385_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
