"""Tests for Phase 202: Single-Cell RNA-seq Droplet De-multiplexing & Ambient RNA Scrubber Engine Repo."""

import pytest
from database.repositories.scrnaseq_ambient_scrubber_repo import ScRNASeqAmbientScrubberRepository


@pytest.mark.asyncio
async def test_scrnaseq_ambient_scrubber_repository(db_session):
    repo = ScRNASeqAmbientScrubberRepository(db_session)

    study = await repo.create_study(
        name="Study_202_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="scRNA-seq Ambient RNA Scrubber",
        ambient_rna_contamination_fraction=0.042,
        doublet_detection_auc=0.984,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 202 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_202_Verification"
    assert getattr(study, "ambient_rna_contamination_fraction") == 0.042

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Contaminating Ambient Hemoglobin mRNA Cluster [HBA1/HBB Soup]",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Contaminating Ambient Hemoglobin mRNA Cluster [HBA1/HBB Soup]"

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
    assert fetched.name == "Study_202_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
