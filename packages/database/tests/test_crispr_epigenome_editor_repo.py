"""Tests for Phase 365: Autonomous Ultra-High Throughput CRISPR Epigenome Editing dCas9-DNMT3A/TET1 Methylation Writer/Eraser Repo."""

import pytest
from database.repositories.crispr_epigenome_editor_repo import CrisprEpigenomeEditorRepository


@pytest.mark.asyncio
async def test_crispr_epigenome_editor_repository(db_session):
    repo = CrisprEpigenomeEditorRepository(db_session)

    study = await repo.create_study(
        name="Study_365_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="crispr-epigenome-editor",
        target_cpg_methylation_alteration_pct=91.5,
        epigenetic_silencing_durability_cell_divisions=45.0,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 365 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_365_Verification"
    assert getattr(study, "target_cpg_methylation_alteration_pct") == 91.5

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="PCSK9_Promoter_Targeted_DNA_Hypermethylation_Silencer",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "PCSK9_Promoter_Targeted_DNA_Hypermethylation_Silencer"

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
    assert fetched.name == "Study_365_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
