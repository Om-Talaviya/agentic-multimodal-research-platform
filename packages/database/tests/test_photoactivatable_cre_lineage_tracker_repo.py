"""Tests for Phase 479: Autonomous Optogenetic Photoactivatable Cre-Lox Recombinase Genomic Barcode Lineage Tracker Repo."""

import pytest
from database.repositories.photoactivatable_cre_lineage_tracker_repo import PhotoactivatableCreLineageTrackerRepository


@pytest.mark.asyncio
async def test_photoactivatable_cre_lineage_tracker_repository(db_session):
    repo = PhotoactivatableCreLineageTrackerRepository(db_session)

    study = await repo.create_study(
        name="Study_479_Verification",
        target_specimen="Split Magnet-Cre Recombinase Knock-In Neural Crest Stem Cell Line with LoxP Barcode Cassette",
        analytical_modality="photoactivatable-cre-lineage-tracking",
        photoinduction_recombination_efficiency=0.925,
        dark_state_leakage_recombination_rate=0.0012,
        spatial_focal_lineage_resolution_um=1.25,
        clonal_barcode_diversity_entropy=8.45,
        confidence_score=0.994,
        status="completed",
        summary_report="Phase 479 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_479_Verification"
    assert study.photoinduction_recombination_efficiency == 0.925

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Opto_Cre_LoxP_DNA_Excision_Barcoding",
        profile_category="Primary Step",
        quantitative_value=0.925,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Opto_Cre_LoxP_DNA_Excision_Barcoding"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="photoinduction_recombination_efficiency",
        observed_value=0.925,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 0.925

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_479_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
