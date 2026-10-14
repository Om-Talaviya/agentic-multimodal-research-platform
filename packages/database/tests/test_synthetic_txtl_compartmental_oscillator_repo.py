"""Tests for Phase 488: Autonomous Cell-Free Compartmentalized Synthetic Transcription-Translation (TX-TL) Feedback Oscillator Repo."""

import pytest
from database.repositories.synthetic_txtl_compartmental_oscillator_repo import SyntheticTxtlCompartmentalOscillatorRepository


@pytest.mark.asyncio
async def test_synthetic_txtl_compartmental_oscillator_repository(db_session):
    repo = SyntheticTxtlCompartmentalOscillatorRepository(db_session)

    study = await repo.create_study(
        name="Study_488_Verification",
        target_specimen="Continuous Microfluidic Droplet-Exchanged E. coli Cell-Free Expression Matrix with Repressilator Circuit",
        analytical_modality="txtl-compartmental-oscillator",
        oscillation_periodicity_hours=3.4,
        peak_to_trough_amplitude_fold_change=18.5,
        atp_regeneration_flux_mM_per_hr=1.8,
        oscillation_undamped_cycle_count=24.0,
        confidence_score=0.99,
        status="completed",
        summary_report="Phase 488 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_488_Verification"
    assert study.oscillation_periodicity_hours == 3.4

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Cascaded_TetR_cI_LacI_Protein_Synthesis_Burst",
        profile_category="Primary Step",
        quantitative_value=3.4,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Cascaded_TetR_cI_LacI_Protein_Synthesis_Burst"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="oscillation_periodicity_hours",
        observed_value=3.4,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 3.4

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_488_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
