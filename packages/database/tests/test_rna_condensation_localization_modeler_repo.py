"""Tests for Phase 321: Autonomous Intracellular RNA Zipcode Localization & Liquid-Liquid Phase Separation Condensate Modeler Repo."""

import pytest
from database.repositories.rna_condensation_localization_modeler_repo import RnaCondensationLocalizationModelerRepository


@pytest.mark.asyncio
async def test_rna_condensation_localization_modeler_repository(db_session):
    repo = RnaCondensationLocalizationModelerRepository(db_session)

    study = await repo.create_study(
        name="Study_321_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="rna-condensation-localization",
        condensate_partition_coefficient_k=48.0,
        motor_protein_binding_affinity_kd_nm=12.4,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 321 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_321_Verification"
    assert getattr(study, "condensate_partition_coefficient_k") == 48.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Neuronal_Axonal_Transport_Zipcode_Motif_Ensemble",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Neuronal_Axonal_Transport_Zipcode_Motif_Ensemble"

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
    assert fetched.name == "Study_321_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
