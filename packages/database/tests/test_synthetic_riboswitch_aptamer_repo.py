"""Tests for Phase 217: Autonomous Synthetic Bio Riboswitch Aptamer Secondary Structure & Ligand-Induced Translation Terminator Engine Repo."""

import pytest
from database.repositories.synthetic_riboswitch_aptamer_repo import SyntheticRiboswitchAptamerRepository


@pytest.mark.asyncio
async def test_synthetic_riboswitch_aptamer_repository(db_session):
    repo = SyntheticRiboswitchAptamerRepository(db_session)

    study = await repo.create_study(
        name="Study_217_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="synthetic-riboswitch-aptamer",
        dynamic_range_fold_induction=18.5,
        switching_free_energy_kcal_mol=-12.4,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 217 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_217_Verification"
    assert getattr(study, "dynamic_range_fold_induction") == 18.5

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Theophylline_Responsive_Riboswitch_Terminator_v3",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Theophylline_Responsive_Riboswitch_Terminator_v3"

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
    assert fetched.name == "Study_217_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
