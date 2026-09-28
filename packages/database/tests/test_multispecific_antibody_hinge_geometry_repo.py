"""Tests for Phase 254: Autonomous Multi-Specific Antibody Fragment Geometry & Hinge Flexibility In-Silico Modeling Engine Repo."""

import pytest
from database.repositories.multispecific_antibody_hinge_geometry_repo import MultispecificAntibodyHingeGeometryRepository


@pytest.mark.asyncio
async def test_multispecific_antibody_hinge_geometry_repository(db_session):
    repo = MultispecificAntibodyHingeGeometryRepository(db_session)

    study = await repo.create_study(
        name="Study_254_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="multispecific-antibody-hinge-geometry",
        simultaneous_dual_binding_efficiency_pct=97.5,
        hinge_flexibility_rmsf_angstrom=4.8,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 254 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_254_Verification"
    assert getattr(study, "simultaneous_dual_binding_efficiency_pct") == 97.5

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="CD3_CD19_Bispecific_T_Cell_Engager_Hinge_Arc",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "CD3_CD19_Bispecific_T_Cell_Engager_Hinge_Arc"

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
    assert fetched.name == "Study_254_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
