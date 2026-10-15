"""Tests for Phase 531: Autonomous Spatially-Resolved Optogenetic Mitochondrial Calcium Spark & Bioenergetics Modeler Repo."""

import pytest
from database.repositories.optogenetic_mitochondrial_calcium_oscillator_repo import OptogeneticMitochondrialCalciumOscillatorRepository


@pytest.mark.asyncio
async def test_optogenetic_mitochondrial_calcium_oscillator_repository(db_session):
    repo = OptogeneticMitochondrialCalciumOscillatorRepository(db_session)

    study = await repo.create_study(
        name="Study_531_Verification",
        target_specimen="Human Cardiomyocyte Syncytium with Mitochondrially-Targeted ChR2 and R-GECO1 Probes",
        analytical_modality="optogenetic-mitochondrial-calcium",
        matrix_calcium_influx_rate_uM_per_s=12.4,
        mcu_channel_open_probability=0.84,
        atp_production_coupling_gain_pct=28.5,
        mptp_opening_prevention_threshold_uM=4.2,
        confidence_score=0.993,
        status="completed",
        summary_report="Phase 531 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_531_Verification"
    assert study.matrix_calcium_influx_rate_uM_per_s == 12.4

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Mitochondrial_Cristae_Calcium_Microdomain_Spark",
        profile_category="Primary Step",
        quantitative_value=12.4,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Mitochondrial_Cristae_Calcium_Microdomain_Spark"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="matrix_calcium_influx_rate_uM_per_s",
        observed_value=12.4,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 12.4

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_531_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
