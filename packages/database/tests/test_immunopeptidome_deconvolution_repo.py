"""Tests for Phase 213: Autonomous Mass Spectrometry Immunopeptidomics & Non-Canonical Cryptic Peptide Deconvolution Engine Repo."""

import pytest
from database.repositories.immunopeptidome_deconvolution_repo import ImmunopeptidomeDeconvolutionRepository


@pytest.mark.asyncio
async def test_immunopeptidome_deconvolution_repository(db_session):
    repo = ImmunopeptidomeDeconvolutionRepository(db_session)

    study = await repo.create_study(
        name="Study_213_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="immunopeptidome-deconvolution",
        spectral_identification_fdr_pct=0.85,
        presentation_affinity_nM=18.4,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 213 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_213_Verification"
    assert getattr(study, "spectral_identification_fdr_pct") == 0.85

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="HLA_A0201_Cryptic_5UTR_Peptide_SLYNTVATL",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "HLA_A0201_Cryptic_5UTR_Peptide_SLYNTVATL"

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
    assert fetched.name == "Study_213_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
