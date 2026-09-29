"""Tests for Phase 297: Autonomous In-Silico Multi-Specific Nanobody (VHH) Paratope Rigid-Body Conformation Forecaster Repo."""

import pytest
from database.repositories.nanobody_vhh_paratope_design_repo import NanobodyVhhParatopeDesignRepository


@pytest.mark.asyncio
async def test_nanobody_vhh_paratope_design_repository(db_session):
    repo = NanobodyVhhParatopeDesignRepository(db_session)

    study = await repo.create_study(
        name="Study_297_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="nanobody-vhh-paratope-design",
        vhh_antigen_binding_affinity_retention_pct=98.6,
        cdr3_loop_conformation_rmsd_angstrom=1.1,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 297 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_297_Verification"
    assert getattr(study, "vhh_antigen_binding_affinity_retention_pct") == 98.6

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Anti_SARS_CoV_2_Neutralizing_VHH_Tri_Body",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Anti_SARS_CoV_2_Neutralizing_VHH_Tri_Body"

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
    assert fetched.name == "Study_297_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
