"""Tests for Phase 282: Autonomous Single-Cell Chromatin Conformation (scHi-C) 3D Loop & Topologically Associating Domain Engine Repo."""

import pytest
from database.repositories.single_cell_hic_3d_chromatin_loop_repo import SingleCellHic3dChromatinLoopRepository


@pytest.mark.asyncio
async def test_single_cell_hic_3d_chromatin_loop_repository(db_session):
    repo = SingleCellHic3dChromatinLoopRepository(db_session)

    study = await repo.create_study(
        name="Study_282_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="single-cell-hic-3d-chromatin-loop",
        single_cell_tad_boundary_precision_score=95.6,
        chromatin_loop_contact_enrichment_fold=7.4,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 282 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_282_Verification"
    assert getattr(study, "single_cell_tad_boundary_precision_score") == 95.6

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Embryonic_Stem_Cell_Pluripotency_Locus_scHiC_Loop",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Embryonic_Stem_Cell_Pluripotency_Locus_scHiC_Loop"

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
    assert fetched.name == "Study_282_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
