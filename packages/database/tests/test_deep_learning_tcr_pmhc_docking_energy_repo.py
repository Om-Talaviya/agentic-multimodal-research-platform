"""Tests for Phase 514: Autonomous Equivariant Graph Neural Network TCR-pMHC Interface Binding Energy Forecaster Repo."""

import pytest
from database.repositories.deep_learning_tcr_pmhc_docking_energy_repo import DeepLearningTcrPmhcDockingEnergyRepository


@pytest.mark.asyncio
async def test_deep_learning_tcr_pmhc_docking_energy_repository(db_session):
    repo = DeepLearningTcrPmhcDockingEnergyRepository(db_session)

    study = await repo.create_study(
        name="Study_514_Verification",
        target_specimen="Structure-Resolved Complex of Human CD8+ TCR with Cancer-Testis Neoantigen NY-ESO-1 HLA-A*02:01",
        analytical_modality="egnn-tcr-pmhc-docking",
        predicted_binding_free_energy_delta_G_kcal_mol=-10.45,
        cdr3_loop_interface_contact_rmsd_angstrom=0.85,
        allotype_cross_reactivity_prediction_auroc=0.965,
        dissociation_constant_kd_nM=45.0,
        confidence_score=0.995,
        status="completed",
        summary_report="Phase 514 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_514_Verification"
    assert study.predicted_binding_free_energy_delta_G_kcal_mol == -10.45

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="CDR3beta_Apex_Peptide_Pocket_Hydrogen_Bond_Network",
        profile_category="Primary Step",
        quantitative_value=-10.45,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "CDR3beta_Apex_Peptide_Pocket_Hydrogen_Bond_Network"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="predicted_binding_free_energy_delta_G_kcal_mol",
        observed_value=-10.45,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == -10.45

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_514_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
