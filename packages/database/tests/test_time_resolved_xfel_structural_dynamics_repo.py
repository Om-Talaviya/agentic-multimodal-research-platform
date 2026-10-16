"""Tests for Phase 557: Autonomous Time-Resolved Femtosecond X-ray Free-Electron Laser (XFEL) Macromolecular Structural Dynamics Engine Repo."""

import pytest
from database.repositories.time_resolved_xfel_structural_dynamics_repo import TimeResolvedXfelStructuralDynamicsRepository


@pytest.mark.asyncio
async def test_time_resolved_xfel_structural_dynamics_repository(db_session):
    repo = TimeResolvedXfelStructuralDynamicsRepository(db_session)

    study = await repo.create_study(
        name="Study_557_Verification",
        target_specimen="Photoactive Yellow Protein (PYP) Microcrystals probed by 10-fs X-ray Pulses at LCLS-II after 450nm Laser Photolysis",
        analytical_modality="time-resolved-xfel-dynamics",
        femtosecond_temporal_resolution_fs=85.0,
        chromophore_trans_to_cis_isomerization_time_ps=1.45,
        difference_electron_density_signal_snr=28.5,
        serial_femtosecond_crystallography_resolution_a=1.35,
        confidence_score=0.997,
        status="completed",
        summary_report="Phase 557 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_557_Verification"
    assert study.femtosecond_temporal_resolution_fs == 85.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="PYP_pG_to_pR_Photolyzed_Intermediate_Density_Wave",
        profile_category="Primary Step",
        quantitative_value=85.0,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "PYP_pG_to_pR_Photolyzed_Intermediate_Density_Wave"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="femtosecond_temporal_resolution_fs",
        observed_value=85.0,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 85.0

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_557_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
