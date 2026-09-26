"""Tests for Phase 214: Autonomous Cryo-EM Continuous Flexible Backbone Motion & Deep Non-Rigid Fitting Engine Repo."""

import pytest
from database.repositories.cryoem_flexible_backbone_refine_repo import CryoEMFlexibleBackboneRefineRepository


@pytest.mark.asyncio
async def test_cryoem_flexible_backbone_refine_repository(db_session):
    repo = CryoEMFlexibleBackboneRefineRepository(db_session)

    study = await repo.create_study(
        name="Study_214_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="cryoem-flexible-backbone-refine",
        density_cross_correlation=0.942,
        backbone_rmsd_angstrom=1.15,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 214 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_214_Verification"
    assert getattr(study, "density_cross_correlation") == 0.942

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Ribosome_Translocation_Conformational_Arc",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Ribosome_Translocation_Conformational_Arc"

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
    assert fetched.name == "Study_214_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
