"""Tests for Phase 447: Autonomous Coarse-Grained DNA-Protein Complex Martini Force-Field Molecular Dynamics Simulator Repo."""

import pytest
from database.repositories.coarse_grained_martini_dna_protein_repo import CoarseGrainedMartiniDnaProteinRepository


@pytest.mark.asyncio
async def test_coarse_grained_martini_dna_protein_repository(db_session):
    repo = CoarseGrainedMartiniDnaProteinRepository(db_session)

    study = await repo.create_study(
        name="Study_447_Verification",
        target_specimen="Nucleosome Core Particle Octamer with 147bp Wrapped DNA in 150mM Salt Solvation Box",
        analytical_modality="coarse-grained-martini-dynamics",
        bead_rmsd_convergence_angstrom=2.15,
        electrostatic_solvation_free_energy_kcal_mol=-342.5,
        conformational_sampling_speedup_factor=85.0,
        contact_pair_distribution_g_r=1.48,
        confidence_score=0.993,
        status="completed",
        summary_report="Phase 447 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_447_Verification"
    assert study.bead_rmsd_convergence_angstrom == 2.15

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Martini_Bead_Electrostatic_Equilibration_Step",
        profile_category="Primary Step",
        quantitative_value=2.15,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Martini_Bead_Electrostatic_Equilibration_Step"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="bead_rmsd_convergence_angstrom",
        observed_value=2.15,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 2.15

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_447_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
