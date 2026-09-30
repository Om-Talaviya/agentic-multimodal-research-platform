"""Tests for Phase 391: Autonomous Therapeutic Monoclonal Antibody Fc Glycoengineering & ADCC Effector Enhancer Repo."""

import pytest
from database.repositories.antibody_fc_glycoengineering_repo import AntibodyFcGlycoengineeringRepository


@pytest.mark.asyncio
async def test_antibody_fc_glycoengineering_repository(db_session):
    repo = AntibodyFcGlycoengineeringRepository(db_session)

    study = await repo.create_study(
        name="Study_391_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="antibody-fc-glycoengineering",
        fc_gamma_receptor_iiia_binding_affinity_increase_fold=52.0,
        antibody_dependent_cellular_cytotoxicity_adcc_lysis_pct=88.5,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 391 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_391_Verification"
    assert getattr(study, "fc_gamma_receptor_iiia_binding_affinity_increase_fold") == 52.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Afucosylated_Anti_CD20_Obinutuzumab_Fc_Glycoform_Optimization",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Afucosylated_Anti_CD20_Obinutuzumab_Fc_Glycoform_Optimization"

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
    assert fetched.name == "Study_391_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
