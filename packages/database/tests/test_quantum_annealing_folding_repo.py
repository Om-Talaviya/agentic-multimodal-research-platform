"""Tests for Phase 351: Autonomous Quantum Annealing Biomolecular Folding & Energy Landscape Explorer Repo."""

import pytest
from database.repositories.quantum_annealing_folding_repo import QuantumAnnealingFoldingRepository


@pytest.mark.asyncio
async def test_quantum_annealing_folding_repository(db_session):
    repo = QuantumAnnealingFoldingRepository(db_session)

    study = await repo.create_study(
        name="Study_351_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="quantum-annealing-folding",
        ground_state_energy_minimization_kcal_mol=-428.5,
        quantum_annealing_success_probability_pct=98.4,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 351 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_351_Verification"
    assert getattr(study, "ground_state_energy_minimization_kcal_mol") == -428.5

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Amyloid_Beta_42_Fibril_Nucleation_QUBO_Folding_Lattice",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Amyloid_Beta_42_Fibril_Nucleation_QUBO_Folding_Lattice"

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
    assert fetched.name == "Study_351_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
