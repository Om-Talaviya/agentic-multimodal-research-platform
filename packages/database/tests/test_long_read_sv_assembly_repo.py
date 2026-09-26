"""Tests for Phase 208: Long-Read Structural Variant & De Novo Assembly Engine Repo."""

import pytest
from database.repositories.long_read_sv_assembly_repo import LongReadSVAssemblyRepository


@pytest.mark.asyncio
async def test_long_read_sv_assembly_repository(db_session):
    repo = LongReadSVAssemblyRepository(db_session)

    study = await repo.create_study(
        name="Study_208_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="Long-Read SV Assembly",
        contig_n50_megabases=38.5,
        structural_variant_breakpoint_precision_bp=1.2,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 208 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_208_Verification"
    assert getattr(study, "contig_n50_megabases") == 38.5

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Translocation Breakpoint Junction [t(9;22) BCR-ABL1 Fusion]",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Translocation Breakpoint Junction [t(9;22) BCR-ABL1 Fusion]"

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
    assert fetched.name == "Study_208_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
