"""Tests for Phase 228: Autonomous TCR-pMHC Complex Interface Geometric Docking & Cross-Reactivity Risk Engine Repo."""

import pytest
from database.repositories.tcr_pmhc_docking_affinity_landscape_repo import TcrPmhcDockingAffinityLandscapeRepository


@pytest.mark.asyncio
async def test_tcr_pmhc_docking_affinity_landscape_repository(db_session):
    repo = TcrPmhcDockingAffinityLandscapeRepository(db_session)

    study = await repo.create_study(
        name="Study_228_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="tcr-pmhc-docking-affinity-landscape",
        binding_affinity_kd_uM=4.2,
        cross_reactivity_safety_index=99.1,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 228 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_228_Verification"
    assert getattr(study, "binding_affinity_kd_uM") == 4.2

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="NY_ESO_1_157_165_1G4_TCR_HLA_A0201_Complex",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "NY_ESO_1_157_165_1G4_TCR_HLA_A0201_Complex"

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
    assert fetched.name == "Study_228_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
