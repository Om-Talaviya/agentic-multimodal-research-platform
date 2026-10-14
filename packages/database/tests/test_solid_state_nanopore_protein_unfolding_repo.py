"""Tests for Phase 508: Autonomous Solid-State Nanopore Single-Molecule Protein Co-Translocational Unfolding Modeler Repo."""

import pytest
from database.repositories.solid_state_nanopore_protein_unfolding_repo import SolidStateNanoporeProteinUnfoldingRepository


@pytest.mark.asyncio
async def test_solid_state_nanopore_protein_unfolding_repository(db_session):
    repo = SolidStateNanoporeProteinUnfoldingRepository(db_session)

    study = await repo.create_study(
        name="Study_508_Verification",
        target_specimen="Sub-3nm Low-Noise HfO2 Nanopore with ClpX-Coupled Maltose-Binding Protein Translocation",
        analytical_modality="nanopore-protein-unfolding",
        unfolding_energy_barrier_height_kbT=24.5,
        translocation_dwell_time_per_domain_ms=8.2,
        residual_current_fraction_blockade=0.765,
        single_amino_acid_substitutional_snr=16.5,
        confidence_score=0.993,
        status="completed",
        summary_report="Phase 508 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_508_Verification"
    assert study.unfolding_energy_barrier_height_kbT == 24.5

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="ClpX_Mechanical_Pull_Polypeptide_Threading",
        profile_category="Primary Step",
        quantitative_value=24.5,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "ClpX_Mechanical_Pull_Polypeptide_Threading"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="unfolding_energy_barrier_height_kbT",
        observed_value=24.5,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 24.5

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_508_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
