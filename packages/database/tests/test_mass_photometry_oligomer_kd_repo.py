"""Tests for Phase 426: Autonomous Mass Photometry Macromolecular Oligomeric Mass Distribution & Dissociation Constant (KD) Estimator Repo."""

import pytest
from database.repositories.mass_photometry_oligomer_kd_repo import MassPhotometryOligomerKdRepository


@pytest.mark.asyncio
async def test_mass_photometry_oligomer_kd_repository(db_session):
    repo = MassPhotometryOligomerKdRepository(db_session)

    study = await repo.create_study(
        name="Study_426_Verification",
        target_specimen="Native Macromolecular Assembly on Glass Coverslip Surface",
        analytical_modality="mass-photometry-kd",
        molecular_mass_kda=148.5,
        equilibrium_dissociation_constant_nM=18.4,
        dimer_to_monomer_peak_ratio=2.85,
        contrast_interferometry_snr=42.6,
        confidence_score=0.992,
        status="completed",
        summary_report="Phase 426 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_426_Verification"
    assert study.molecular_mass_kda == 148.5

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Interferometric_Scattering_Mass_Peak",
        profile_category="Primary Step",
        quantitative_value=148.5,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Interferometric_Scattering_Mass_Peak"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="molecular_mass_kda",
        observed_value=148.5,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 148.5

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_426_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
