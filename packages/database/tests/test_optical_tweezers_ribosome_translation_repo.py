"""Tests for Phase 451: Autonomous Single-Molecule Optical Tweezers Ribosome Translation Kinetic Polypeptide Translocation Engine Repo."""

import pytest
from database.repositories.optical_tweezers_ribosome_translation_repo import OpticalTweezersRibosomeTranslationRepository


@pytest.mark.asyncio
async def test_optical_tweezers_ribosome_translation_repository(db_session):
    repo = OpticalTweezersRibosomeTranslationRepository(db_session)

    study = await repo.create_study(
        name="Study_451_Verification",
        target_specimen="70S Bacterial Ribosome Translating Structured mRNA Stem-Loop under Constant Force (12 pN)",
        analytical_modality="ribosome-translation-dynamics",
        codon_stepping_dwell_time_ms=68.4,
        mrna_unfolding_barrier_activation_energy_kb_t=14.8,
        frameshift_slippage_probability=0.0035,
        elongation_rate_amino_acids_per_s=14.6,
        confidence_score=0.994,
        status="completed",
        summary_report="Phase 451 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_451_Verification"
    assert study.codon_stepping_dwell_time_ms == 68.4

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Single_Codon_Tri-Nucleotide_Stepping_Transition",
        profile_category="Primary Step",
        quantitative_value=68.4,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Single_Codon_Tri-Nucleotide_Stepping_Transition"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="codon_stepping_dwell_time_ms",
        observed_value=68.4,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 68.4

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_451_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
