"""Tests for Phase 370: Autonomous Deep Immunoglobulin Repertoire (Rep-Seq) Somatic Hypermutation Lineage Tree Reconstructor Repo."""

import pytest
from database.repositories.repseq_shm_lineage_tree_repo import RepseqShmLineageTreeRepository


@pytest.mark.asyncio
async def test_repseq_shm_lineage_tree_repository(db_session):
    repo = RepseqShmLineageTreeRepository(db_session)

    study = await repo.create_study(
        name="Study_370_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="repseq-shm-lineage-tree",
        clonal_lineage_reconstruction_parsimony_score=98.6,
        somatic_hypermutation_rate_mutations_per_kb=24.5,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 370 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_370_Verification"
    assert getattr(study, "clonal_lineage_reconstruction_parsimony_score") == 98.6

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Broadly_Neutralizing_HIV_VRC01_Class_Lineage_Phylogeny",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Broadly_Neutralizing_HIV_VRC01_Class_Lineage_Phylogeny"

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
    assert fetched.name == "Study_370_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
