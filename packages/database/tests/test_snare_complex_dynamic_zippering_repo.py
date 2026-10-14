"""Tests for Phase 487: Autonomous Synaptic Vesicle SNARE Complex Dynamic Zippering & Neurotransmitter Release Predictor Repo."""

import pytest
from database.repositories.snare_complex_dynamic_zippering_repo import SnareComplexDynamicZipperingRepository


@pytest.mark.asyncio
async def test_snare_complex_dynamic_zippering_repository(db_session):
    repo = SnareComplexDynamicZipperingRepository(db_session)

    study = await repo.create_study(
        name="Study_487_Verification",
        target_specimen="Reconstituted Proteoliposome Single-Vesicle Synaptobrevin-2 / Syntaxin-1A / SNAP-25 Assembly",
        analytical_modality="snare-complex-zippering",
        snare_zippering_free_energy_kbT=35.0,
        membrane_fusion_pore_opening_time_ms=0.85,
        synaptotagmin_ca2_activation_threshold_uM=12.5,
        vesicle_docking_priming_probability=0.942,
        confidence_score=0.993,
        status="completed",
        summary_report="Phase 487 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_487_Verification"
    assert study.snare_zippering_free_energy_kbT == 35.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Four_Helix_Bundle_Trans_To_Cis_Transition",
        profile_category="Primary Step",
        quantitative_value=35.0,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Four_Helix_Bundle_Trans_To_Cis_Transition"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="snare_zippering_free_energy_kbT",
        observed_value=35.0,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 35.0

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_487_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
