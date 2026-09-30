"""Tests for Phase 411: Single-Cell Mitochondrial Bioenergetics & OCR/ECAR Metabolic Flux Balance Simulator Repo."""

import pytest
from database.repositories.mitochondrial_metabolism_flux_repo import MitochondrialMetabolismFluxRepository


@pytest.mark.asyncio
async def test_mitochondrial_metabolism_flux_repository(db_session):
    repo = MitochondrialMetabolismFluxRepository(db_session)

    study = await repo.create_study(
        name="Study_411_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="mitochondrial-metabolism-flux",
        oxygen_consumption_rate_ocr_pmol_per_min=185.0,
        mitochondrial_spare_respiratory_capacity_ratio=3.42,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 411 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_411_Verification"
    assert getattr(study, "oxygen_consumption_rate_ocr_pmol_per_min") == 185.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Complex_I_IV_Oxidative_Phosphorylation_ATP_Synthesis_Loop",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Complex_I_IV_Oxidative_Phosphorylation_ATP_Synthesis_Loop"

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
    assert fetched.name == "Study_411_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
