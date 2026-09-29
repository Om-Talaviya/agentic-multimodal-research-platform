"""Tests for Phase 358: Autonomous High-Density Microelectrode Array (HD-MEA) Cortical Organoid Synaptic Plasticity Analyzer Repo."""

import pytest
from database.repositories.hd_mea_organoid_plasticity_repo import HdMeaOrganoidPlasticityRepository


@pytest.mark.asyncio
async def test_hd_mea_organoid_plasticity_repository(db_session):
    repo = HdMeaOrganoidPlasticityRepository(db_session)

    study = await repo.create_study(
        name="Study_358_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="hd-mea-organoid-plasticity",
        synaptic_plasticity_potentiation_ratio_fold=2.45,
        cross_frequency_theta_gamma_coupling_index=0.88,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 358 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_358_Verification"
    assert getattr(study, "synaptic_plasticity_potentiation_ratio_fold") == 2.45

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Cortical_Organoid_26000_Electrode_STDP_Plasticity_Grid",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Cortical_Organoid_26000_Electrode_STDP_Plasticity_Grid"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="Sensitivity & Recovery Rate",
        observed_value=0.984,
        z_score=2.85,
        p_value=0.00012,
    )
    assert trace.id is not None
    assert trace.observed_value == 0.984

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_358_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
