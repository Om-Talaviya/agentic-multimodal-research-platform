"""Tests for Phase 517: Autonomous Dual-Color Multiplexed Optogenetic Neocortical Oscillatory Synchrony Mapper Repo."""

import pytest
from database.repositories.multiplexed_optogenetic_neocortical_synchrony_repo import MultiplexedOptogeneticNeocorticalSynchronyRepository


@pytest.mark.asyncio
async def test_multiplexed_optogenetic_neocortical_synchrony_repository(db_session):
    repo = MultiplexedOptogeneticNeocorticalSynchronyRepository(db_session)

    study = await repo.create_study(
        name="Study_517_Verification",
        target_specimen="Transgenic Mouse Somatosensory Cortex expressing ChRmine (Red) and ChETA (Blue) in Layer 2/3 and 5",
        analytical_modality="dual-color-optogenetic-synchrony",
        gamma_band_phase_locking_value_plv=0.895,
        optical_crosstalk_attenuation_ratio=42.0,
        spike_timing_jitter_precision_std_ms=0.45,
        cross_layer_laminar_information_transfer_entropy=0.68,
        confidence_score=0.993,
        status="completed",
        summary_report="Phase 517 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_517_Verification"
    assert study.gamma_band_phase_locking_value_plv == 0.895

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Red_Shifted_Deep_Tissue_Layer5_Photostimulation",
        profile_category="Primary Step",
        quantitative_value=0.895,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Red_Shifted_Deep_Tissue_Layer5_Photostimulation"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="gamma_band_phase_locking_value_plv",
        observed_value=0.895,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 0.895

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_517_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
