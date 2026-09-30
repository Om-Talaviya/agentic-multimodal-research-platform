"""Tests for Phase 379: Autonomous Synthetic Microbial Electrosynthesis & Biocathode Electron Transfer Engine Repo."""

import pytest
from database.repositories.microbial_electrosynthesis_engine_repo import MicrobialElectrosynthesisEngineRepository


@pytest.mark.asyncio
async def test_microbial_electrosynthesis_engine_repository(db_session):
    repo = MicrobialElectrosynthesisEngineRepository(db_session)

    study = await repo.create_study(
        name="Study_379_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="microbial-electrosynthesis-engine",
        faradaic_electron_transfer_efficiency_pct=92.5,
        biocathode_volumetric_acetate_production_g_l_day=14.8,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 379 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_379_Verification"
    assert getattr(study, "faradaic_electron_transfer_efficiency_pct") == 92.5

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Sporomusa_ovata_Electrically_Driven_Acetate_Bioreactor",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Sporomusa_ovata_Electrically_Driven_Acetate_Bioreactor"

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
    assert fetched.name == "Study_379_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
