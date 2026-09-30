"""Tests for Phase 396: Membrane Protein Lipid Nanodisc Molecular Dynamics Markov State Modeler Repo."""

import pytest
from database.repositories.membrane_protein_nanodisc_msm_repo import MembraneProteinNanodiscMsmRepository


@pytest.mark.asyncio
async def test_membrane_protein_nanodisc_msm_repository(db_session):
    repo = MembraneProteinNanodiscMsmRepository(db_session)

    study = await repo.create_study(
        name="Study_396_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="membrane-protein-nanodisc-msm",
        conformation_free_energy_barrier_kcal_mol=4.15,
        markov_state_transition_rate_per_microsec=12.8,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 396 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_396_Verification"
    assert getattr(study, "conformation_free_energy_barrier_kcal_mol") == 4.15

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="GPCR_Beta2AR_Active_Gprotein_Coupled_Nanodisc_State",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "GPCR_Beta2AR_Active_Gprotein_Coupled_Nanodisc_State"

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
    assert fetched.name == "Study_396_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
