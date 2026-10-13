"""Tests for Phase 454: Autonomous Synthetic Cell-Free Compartmentalized Gene Circuit Quorum Feedback Oscillator Repo."""

import pytest
from database.repositories.cell_free_quorum_feedback_oscillator_repo import CellFreeQuorumFeedbackOscillatorRepository


@pytest.mark.asyncio
async def test_cell_free_quorum_feedback_oscillator_repository(db_session):
    repo = CellFreeQuorumFeedbackOscillatorRepository(db_session)

    study = await repo.create_study(
        name="Study_454_Verification",
        target_specimen="Micro-Emulsion Lipid Vesicles with LuxI/LuxR Synthetic Transcriptional Auto-Inducer Network",
        analytical_modality="cell-free-quorum-oscillator",
        quorum_oscillation_periodicity_hours=3.45,
        ahl_autoinducer_diffusion_flux_umol_cm2_s=0.082,
        inter_compartment_synchronization_index=0.945,
        circuit_persistence_lifetime_hours=42.0,
        confidence_score=0.987,
        status="completed",
        summary_report="Phase 454 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_454_Verification"
    assert study.quorum_oscillation_periodicity_hours == 3.45

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="LuxR_Promoter_Autoinduction_Limit_Cycle",
        profile_category="Primary Step",
        quantitative_value=3.45,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "LuxR_Promoter_Autoinduction_Limit_Cycle"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="quorum_oscillation_periodicity_hours",
        observed_value=3.45,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 3.45

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_454_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
