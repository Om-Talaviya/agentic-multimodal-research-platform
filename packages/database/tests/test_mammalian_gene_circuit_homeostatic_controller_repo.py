"""Tests for Phase 556: Autonomous Synthetic Mammalian Gene Circuit Feedback Integral Controller for Homeostatic Glucose Regulation Repo."""

import pytest
from database.repositories.mammalian_gene_circuit_homeostatic_controller_repo import MammalianGeneCircuitHomeostaticControllerRepository


@pytest.mark.asyncio
async def test_mammalian_gene_circuit_homeostatic_controller_repository(db_session):
    repo = MammalianGeneCircuitHomeostaticControllerRepository(db_session)

    study = await repo.create_study(
        name="Study_556_Verification",
        target_specimen="Engineered Beta-Cell Like HEK-293T cells expressing Synthetic Glucose-Sensing Integral Antithetic Feedback Invertible Controller",
        analytical_modality="synthetic-homeostatic-circuit",
        homeostatic_glucose_setpoint_steady_state_mg_dl=95.0,
        integral_control_settling_time_minutes=42.0,
        steady_state_error_offset_pct=0.45,
        insulin_secretion_burst_amplitude_pg_cell=18.2,
        confidence_score=0.998,
        status="completed",
        summary_report="Phase 556 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_556_Verification"
    assert study.homeostatic_glucose_setpoint_steady_state_mg_dl == 95.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Antithetic_Molecular_Sequestration_Controller_Pair",
        profile_category="Primary Step",
        quantitative_value=95.0,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Antithetic_Molecular_Sequestration_Controller_Pair"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="homeostatic_glucose_setpoint_steady_state_mg_dl",
        observed_value=95.0,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 95.0

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_556_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
