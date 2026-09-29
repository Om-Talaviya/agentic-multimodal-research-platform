"""Tests for Phase 276: Autonomous Targeted RNA Cleavage Ribonuclease Targeting Chimera (RIBOTAC) Molecular Design Engine Repo."""

import pytest
from database.repositories.ribotac_rna_cleavage_design_repo import RibotacRnaCleavageDesignRepository


@pytest.mark.asyncio
async def test_ribotac_rna_cleavage_design_repository(db_session):
    repo = RibotacRnaCleavageDesignRepository(db_session)

    study = await repo.create_study(
        name="Study_276_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="ribotac-rna-cleavage-design",
        target_rna_degradation_ec50_nM=18.2,
        off_target_transcriptome_cleavage_fdr_pct=0.04,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 276 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_276_Verification"
    assert getattr(study, "target_rna_degradation_ec50_nM") == 18.2

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Oncogenic_microRNA_21_Targeted_RIBOTAC_Degrader",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Oncogenic_microRNA_21_Targeted_RIBOTAC_Degrader"

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
    assert fetched.name == "Study_276_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
