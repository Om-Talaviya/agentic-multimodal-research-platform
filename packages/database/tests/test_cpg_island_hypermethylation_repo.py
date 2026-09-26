"""Tests for Phase 212: Autonomous Epigenomic Promoter CpG Island Hypermethylation & Tumor Suppressor Gene Silencing Engine Repo."""

import pytest
from database.repositories.cpg_island_hypermethylation_repo import CpGIslandHypermethylationRepository


@pytest.mark.asyncio
async def test_cpg_island_hypermethylation_repository(db_session):
    repo = CpGIslandHypermethylationRepository(db_session)

    study = await repo.create_study(
        name="Study_212_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="cpg-island-hypermethylation",
        silencing_repression_pct=96.7,
        methylation_density_beta=0.89,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 212 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_212_Verification"
    assert getattr(study, "silencing_repression_pct") == 96.7

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="BRCA1_Promoter_CpG_Island_IslandA",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "BRCA1_Promoter_CpG_Island_IslandA"

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
    assert fetched.name == "Study_212_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
