"""Tests for Phase 422: Autonomous Allosteric Ligand Residence Time & Dissociation Rate Constant (k_off) Molecular Dynamics Extractor Repo."""

import pytest
from database.repositories.ligand_residence_time_koff_repo import LigandResidenceTimeKoffRepository


@pytest.mark.asyncio
async def test_ligand_residence_time_koff_repository(db_session):
    repo = LigandResidenceTimeKoffRepository(db_session)

    study = await repo.create_study(
        name="Study_422_Verification",
        target_specimen="Kinase Allosteric Pocket with Type II Small Molecule Inhibitor",
        analytical_modality="residence-time-koff",
        unbinding_rate_koff_s_inv=0.0024,
        residence_time_minutes=416.7,
        dissociation_free_energy_barrier_kcal=21.4,
        binding_pocket_hydration_entropy=-8.6,
        confidence_score=0.984,
        status="completed",
        summary_report="Phase 422 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_422_Verification"
    assert study.unbinding_rate_koff_s_inv == 0.0024

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Allosteric_Pocket_Induced_Fit_Conformation",
        profile_category="Primary Step",
        quantitative_value=0.0024,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Allosteric_Pocket_Induced_Fit_Conformation"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="residence_time_minutes",
        observed_value=0.0024,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 0.0024

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_422_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
