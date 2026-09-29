"""Tests for Phase 330: Autonomous Quantum-Accelerated Molecular Orbital Active Space CASSCF/DMRG Solver Repo."""

import pytest
from database.repositories.quantum_orbital_dmrg_repo import QuantumOrbitalDmrgRepository


@pytest.mark.asyncio
async def test_quantum_orbital_dmrg_repository(db_session):
    repo = QuantumOrbitalDmrgRepository(db_session)

    study = await repo.create_study(
        name="Study_330_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="quantum-orbital-dmrg",
        dmrg_active_space_energy_hartree=-1842.65,
        von_neumann_orbital_entanglement_entropy=2.84,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 330 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_330_Verification"
    assert getattr(study, "dmrg_active_space_energy_hartree") == -1842.65

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Nitrogenase_FeMo_Cofactor_CAS30_30_DMRG_Active_Space",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Nitrogenase_FeMo_Cofactor_CAS30_30_DMRG_Active_Space"

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
    assert fetched.name == "Study_330_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
