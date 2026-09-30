"""Tests for Phase 407: Deep Generative Therapeutic Antibody Humanization & T-Cell Epitope Ranker Repo."""

import pytest
from database.repositories.antibody_humanness_immunogenicity_repo import AntibodyHumannessImmunogenicityRepository


@pytest.mark.asyncio
async def test_antibody_humanness_immunogenicity_repository(db_session):
    repo = AntibodyHumannessImmunogenicityRepository(db_session)

    study = await repo.create_study(
        name="Study_407_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="antibody-humanness-immunogenicity",
        antibody_humanness_t20_score_percentile=96.5,
        mhc_class_ii_immunogenic_epitope_risk_reduction_pct=88.2,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 407 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_407_Verification"
    assert getattr(study, "antibody_humanness_t20_score_percentile") == 96.5

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Murine_CDR_Grafting_Human_IGHV1_69_Germline_Framework",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Murine_CDR_Grafting_Human_IGHV1_69_Germline_Framework"

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
    assert fetched.name == "Study_407_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
