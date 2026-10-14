"""Tests for Phase 516: Autonomous Automated High-Throughput Mass Photometry Macromolecular Mass Dispersity Profiler Repo."""

import pytest
from database.repositories.high_throughput_mass_photometry_ribosome_repo import HighThroughputMassPhotometryRibosomeRepository


@pytest.mark.asyncio
async def test_high_throughput_mass_photometry_ribosome_repository(db_session):
    repo = HighThroughputMassPhotometryRibosomeRepository(db_session)

    study = await repo.create_study(
        name="Study_516_Verification",
        target_specimen="Label-Free Reconstituted 70S Ribosome Assembly Intermediates with Initiation Factors IF1/IF2/IF3",
        analytical_modality="mass-photometry-single-molecule-scattering",
        molecular_mass_resolution_error_pct=1.25,
        subassembly_stoichiometric_ratio_30s_50s_70s=1.05,
        single_molecule_scattering_interferometric_contrast=0.0085,
        sample_consumption_volume_nanoliters=50.0,
        confidence_score=0.994,
        status="completed",
        summary_report="Phase 516 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_516_Verification"
    assert study.molecular_mass_resolution_error_pct == 1.25

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Optical_Interferometric_Scattering_Mass_Peak_Fitting",
        profile_category="Primary Step",
        quantitative_value=1.25,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Optical_Interferometric_Scattering_Mass_Peak_Fitting"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="molecular_mass_resolution_error_pct",
        observed_value=1.25,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 1.25

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_516_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
