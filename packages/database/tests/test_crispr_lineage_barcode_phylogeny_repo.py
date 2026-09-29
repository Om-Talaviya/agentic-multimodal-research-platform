"""Tests for Phase 301: Autonomous Single-Cell Lineage Tracing Multi-Locus CRISPR Barcode Scar Deconvolution & Phylogeny Reconstructor Repo."""

import pytest
from database.repositories.crispr_lineage_barcode_phylogeny_repo import CrisprLineageBarcodePhylogenyRepository


@pytest.mark.asyncio
async def test_crispr_lineage_barcode_phylogeny_repository(db_session):
    repo = CrisprLineageBarcodePhylogenyRepository(db_session)

    study = await repo.create_study(
        name="Study_301_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="crispr-lineage-barcode-phylogeny",
        tree_reconstruction_parsimony_score=96.4,
        lineage_commitment_branching_depth=16.0,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 301 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_301_Verification"
    assert getattr(study, "tree_reconstruction_parsimony_score") == 96.4

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Zebrafish_Embryogenesis_Whole_Organism_Lineage_Tree",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Zebrafish_Embryogenesis_Whole_Organism_Lineage_Tree"

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
    assert fetched.name == "Study_301_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
