"""Tests for Phase 490: Autonomous High-Density CMOS Microelectrode Array Neuromorphic Axonal Conduction Velocity Mapper Repo."""

import pytest
from database.repositories.cmos_mea_axonal_conduction_repo import CmosMeaAxonalConductionRepository


@pytest.mark.asyncio
async def test_cmos_mea_axonal_conduction_repository(db_session):
    repo = CmosMeaAxonalConductionRepository(db_session)

    study = await repo.create_study(
        name="Study_490_Verification",
        target_specimen="Rat Cortical Primary Neurons Cultured over 26,400 Platinum Electrode CMOS Biocompatible Chip",
        analytical_modality="cmos-mea-axonal-conduction",
        axonal_action_potential_conduction_velocity_m_per_s=0.65,
        spike_signal_to_noise_ratio_snr=18.2,
        synaptic_propagation_latency_ms=1.85,
        functional_synaptic_connectivity_density=0.925,
        confidence_score=0.993,
        status="completed",
        summary_report="Phase 490 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_490_Verification"
    assert study.axonal_action_potential_conduction_velocity_m_per_s == 0.65

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Unmyelinated_Axon_Microelectrode_Tracking_Track",
        profile_category="Primary Step",
        quantitative_value=0.65,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Unmyelinated_Axon_Microelectrode_Tracking_Track"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="axonal_action_potential_conduction_velocity_m_per_s",
        observed_value=0.65,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 0.65

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_490_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
