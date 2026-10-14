"""Tests for Phase 493: Autonomous Quantum Coherent Magnetoreception Cryptochrome Radical Pair Dynamics Simulator Repo."""

import pytest
from database.repositories.cryptochrome_radical_pair_magnetoreception_repo import CryptochromeRadicalPairMagnetoreceptionRepository


@pytest.mark.asyncio
async def test_cryptochrome_radical_pair_magnetoreception_repository(db_session):
    repo = CryptochromeRadicalPairMagnetoreceptionRepository(db_session)

    study = await repo.create_study(
        name="Study_493_Verification",
        target_specimen="Purified Migratory Avian Cryptochrome-4 (ErCry4) Flavin-Tryptophan Photoreduced Radical Pair",
        analytical_modality="quantum-radical-pair-magnetoreception",
        singlet_triplet_yield_anisotropy_ratio=1.48,
        radical_pair_quantum_coherence_time_us=4.85,
        geomagnetic_field_inclination_sensitivity_nT=25.0,
        spin_state_entanglement_fidelity=0.982,
        confidence_score=0.993,
        status="completed",
        summary_report="Phase 493 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_493_Verification"
    assert study.singlet_triplet_yield_anisotropy_ratio == 1.48

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Flavin_Tryptophan_Radical_Pair_Zeeman_Splitting",
        profile_category="Primary Step",
        quantitative_value=1.48,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Flavin_Tryptophan_Radical_Pair_Zeeman_Splitting"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="singlet_triplet_yield_anisotropy_ratio",
        observed_value=1.48,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 1.48

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_493_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
