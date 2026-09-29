"""Tests for Phase 335: Autonomous Viral Capsid Cryo-EM Surface Epitope Shielding & Glycan Canopy Modeler Repo."""

import pytest
from database.repositories.capsid_glycan_canopy_shielding_repo import CapsidGlycanCanopyShieldingRepository


@pytest.mark.asyncio
async def test_capsid_glycan_canopy_shielding_repository(db_session):
    repo = CapsidGlycanCanopyShieldingRepository(db_session)

    study = await repo.create_study(
        name="Study_335_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="capsid-glycan-canopy",
        epitope_solvent_accessible_surface_shielding_pct=89.2,
        neutralizing_antibody_steric_clash_score=78.4,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 335 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_335_Verification"
    assert getattr(study, "epitope_solvent_accessible_surface_shielding_pct") == 89.2

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="AAV9_Engineered_Capsid_Neutralizing_Antibody_Evasion_Canopy",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "AAV9_Engineered_Capsid_Neutralizing_Antibody_Evasion_Canopy"

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
    assert fetched.name == "Study_335_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
