"""Tests for Phase 380: Autonomous Proteome-Wide Hydrogen-Deuterium Exchange Mass Spectrometry (HDX-MS) Conformational State Modeler Repo."""

import pytest
from database.repositories.hdx_ms_conformational_modeler_repo import HdxMsConformationalModelerRepository


@pytest.mark.asyncio
async def test_hdx_ms_conformational_modeler_repository(db_session):
    repo = HdxMsConformationalModelerRepository(db_session)

    study = await repo.create_study(
        name="Study_380_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="hdx-ms-conformational-modeler",
        hdx_peptic_peptide_sequence_coverage_pct=99.1,
        deuterium_incorporation_mass_accuracy_ppm=4.5,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 380 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_380_Verification"
    assert getattr(study, "hdx_peptic_peptide_sequence_coverage_pct") == 99.1

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Allosteric_Kinase_Inhibitor_Induced_Conformation_Protection",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Allosteric_Kinase_Inhibitor_Induced_Conformation_Protection"

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
    assert fetched.name == "Study_380_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
