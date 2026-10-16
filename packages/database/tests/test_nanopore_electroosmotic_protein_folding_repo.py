"""Tests for Phase 553: Autonomous Nanopore Electro-Osmotic Trap Protein Native State Unfolding & Refolding Kinetics Modeler Repo."""

import pytest
from database.repositories.nanopore_electroosmotic_protein_folding_repo import NanoporeElectroosmoticProteinFoldingRepository


@pytest.mark.asyncio
async def test_nanopore_electroosmotic_protein_folding_repository(db_session):
    repo = NanoporeElectroosmoticProteinFoldingRepository(db_session)

    study = await repo.create_study(
        name="Study_553_Verification",
        target_specimen="Single Bovine Carbonic Anhydrase II trapped in ClyA Biological Nanopore under Variable Transmembrane Voltage Bias",
        analytical_modality="nanopore-electroosmotic-folding",
        single_molecule_trap_dwell_time_s=14.5,
        electroosmotic_holding_force_pn=8.2,
        unfolding_activation_free_energy_barrier_kt=18.6,
        refolding_transition_rate_per_second=32.4,
        confidence_score=0.995,
        status="completed",
        summary_report="Phase 553 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_553_Verification"
    assert study.single_molecule_trap_dwell_time_s == 14.5

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Intermediate_Molten_Globule_Current_Blockade_State",
        profile_category="Primary Step",
        quantitative_value=14.5,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Intermediate_Molten_Globule_Current_Blockade_State"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="single_molecule_trap_dwell_time_s",
        observed_value=14.5,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 14.5

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_553_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
