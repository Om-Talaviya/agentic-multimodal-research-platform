"""Tests for Phase 562: Autonomous Synthetic Xenobiotic Unnatural Base Pair (UBP: dNaM-d5SICS) DNA Replication Fidelity Forecaster Repo."""

import pytest
from database.repositories.synthetic_xenobiotic_ubp_replication_fidelity_repo import SyntheticXenobioticUbpReplicationFidelityRepository


@pytest.mark.asyncio
async def test_synthetic_xenobiotic_ubp_replication_fidelity_repository(db_session):
    repo = SyntheticXenobioticUbpReplicationFidelityRepository(db_session)

    study = await repo.create_study(
        name="Study_562_Verification",
        target_specimen="Engineered Semi-Synthetic Organism E. coli with dNaM-d5SICS 6-Letter Genetic Alphabet and Nucleoside Triphosphate Transporter",
        analytical_modality="xenobiotic-unnatural-base-pair",
        six_letter_replication_fidelity_pct_per_doubling=99.82,
        ubp_retention_half_life_generations=145.0,
        unnatural_triphosphate_uptake_flux_pmol_min=28.4,
        polymerase_bypass_insertion_efficiency_kcat_km=480000.0,
        confidence_score=0.996,
        status="completed",
        summary_report="Phase 562 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_562_Verification"
    assert study.six_letter_replication_fidelity_pct_per_doubling == 99.82

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="dNaM_d5SICS_Hydrophobic_Packing_Base_Pair_Pocket",
        profile_category="Primary Step",
        quantitative_value=99.82,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "dNaM_d5SICS_Hydrophobic_Packing_Base_Pair_Pocket"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="six_letter_replication_fidelity_pct_per_doubling",
        observed_value=99.82,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 99.82

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_562_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
