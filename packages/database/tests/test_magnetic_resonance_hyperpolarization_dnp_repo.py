"""Tests for Phase 529: Autonomous Dissolution Dynamic Nuclear Polarization (DNP) Hyperpolarized Carbon-13 Flux Tracer Repo."""

import pytest
from database.repositories.magnetic_resonance_hyperpolarization_dnp_repo import MagneticResonanceHyperpolarizationDnpRepository


@pytest.mark.asyncio
async def test_magnetic_resonance_hyperpolarization_dnp_repository(db_session):
    repo = MagneticResonanceHyperpolarizationDnpRepository(db_session)

    study = await repo.create_study(
        name="Study_529_Verification",
        target_specimen="Hyperpolarized [1-13C] Pyruvate with Trityl Radical OX063 Polarized at 1.4K and 5T",
        analytical_modality="dnp-hyperpolarized-nmr-flux",
        carbon_13_nuclear_polarization_pct=46.8,
        in_vivo_t1_relaxation_time_s=45.2,
        pyruvate_to_lactate_apparent_flux_rate_k_pl=0.078,
        spectroscopic_snr_enhancement_factor=14500.0,
        confidence_score=0.995,
        status="completed",
        summary_report="Phase 529 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_529_Verification"
    assert study.carbon_13_nuclear_polarization_pct == 46.8

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Hyperpolarized_Pyruvate_C1_Resonance_Decay",
        profile_category="Primary Step",
        quantitative_value=46.8,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Hyperpolarized_Pyruvate_C1_Resonance_Decay"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="carbon_13_nuclear_polarization_pct",
        observed_value=46.8,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 46.8

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_529_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
