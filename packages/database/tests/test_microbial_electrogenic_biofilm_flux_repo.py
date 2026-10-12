"""Tests for Phase 437: Autonomous Microbial Electrogenic Biofilm Extracellular Electron Transfer (EET) Simulator Repo."""

import pytest
from database.repositories.microbial_electrogenic_biofilm_flux_repo import MicrobialElectrogenicBiofilmRepository


@pytest.mark.asyncio
async def test_microbial_electrogenic_biofilm_flux_repository(db_session):
    repo = MicrobialElectrogenicBiofilmRepository(db_session)

    study = await repo.create_study(
        name="Study_437_Verification",
        target_specimen="Shewanella oneidensis MR-1 Anode Biofilm with Multi-Heme Cytochrome Array",
        analytical_modality="microbial-eet-biofilm",
        current_density_mA_per_cm2=1.42,
        cytochrome_conduction_rate_electrons_per_s=1240.0,
        redox_potential_gradient_mV=-280.0,
        biofilm_coulombic_efficiency=0.895,
        confidence_score=0.986,
        status="completed",
        summary_report="Phase 437 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_437_Verification"
    assert study.current_density_mA_per_cm2 == 1.42

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Multiheme_Conductive_Nanowire_Flux",
        profile_category="Primary Step",
        quantitative_value=1.42,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Multiheme_Conductive_Nanowire_Flux"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="current_density_mA_per_cm2",
        observed_value=1.42,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 1.42

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_437_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
