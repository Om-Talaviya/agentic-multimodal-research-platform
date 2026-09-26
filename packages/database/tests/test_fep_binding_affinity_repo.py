"""Tests for Phase 204: Molecular Dynamics Free Energy Perturbation (FEP) Binding Engine Repo."""

import pytest
from database.repositories.fep_binding_affinity_repo import FEPBindingAffinityRepository


@pytest.mark.asyncio
async def test_fep_binding_affinity_repository(db_session):
    repo = FEPBindingAffinityRepository(db_session)

    study = await repo.create_study(
        name="Study_204_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="MD Free Energy Perturbation FEP",
        relative_binding_free_energy_ddg=-2.48,
        thermodynamic_cycle_hysteresis_error=0.12,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 204 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_204_Verification"
    assert getattr(study, "relative_binding_free_energy_ddg") == -2.48

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Lead Candidate Analog FEP Transformation [ΔΔG = -2.48 kcal/mol]",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Lead Candidate Analog FEP Transformation [ΔΔG = -2.48 kcal/mol]"

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
    assert fetched.name == "Study_204_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
