"""Tests for Phase 319: Autonomous Continuous CRISPR Evolvability Barcode Cellular Lineage Phylogeny Reconstruction Engine Repo."""

import pytest
from database.repositories.lineage_tracing_crispr_phylogeny_repo import LineageTracingCrisprPhylogenyRepository


@pytest.mark.asyncio
async def test_lineage_tracing_crispr_phylogeny_repository(db_session):
    repo = LineageTracingCrisprPhylogenyRepository(db_session)

    study = await repo.create_study(
        name="Study_319_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="lineage-tracing-crispr-phylogeny",
        phylogenetic_tree_robinson_foulds_accuracy_pct=98.6,
        cellular_lineage_barcode_entropy=6.85,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 319 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_319_Verification"
    assert getattr(study, "phylogenetic_tree_robinson_foulds_accuracy_pct") == 98.6

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Embryonic_Organogenesis_Whole_Organism_Lineage_Tree",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Embryonic_Organogenesis_Whole_Organism_Lineage_Tree"

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
    assert fetched.name == "Study_319_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
