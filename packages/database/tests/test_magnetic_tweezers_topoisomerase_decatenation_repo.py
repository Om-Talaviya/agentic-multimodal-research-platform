"""Tests for Phase 484: Autonomous Single-Molecule Magnetic Tweezers Topoisomerase Type II DNA Catenation Decatenator Repo."""

import pytest
from database.repositories.magnetic_tweezers_topoisomerase_decatenation_repo import MagneticTweezersTopoisomeraseDecatenationRepository


@pytest.mark.asyncio
async def test_magnetic_tweezers_topoisomerase_decatenation_repository(db_session):
    repo = MagneticTweezersTopoisomeraseDecatenationRepository(db_session)

    study = await repo.create_study(
        name="Study_484_Verification",
        target_specimen="Tethered Braided DNA Minicircle Pair with Purified Human Topoisomerase II-alpha in Flow Cell",
        analytical_modality="magnetic-tweezers-decatenation",
        decatenation_catalytic_rate_per_sec=3.85,
        atp_hydrolysis_coupling_ratio=1.98,
        t_segment_strand_passage_dwell_time_ms=145.0,
        supercoiling_linking_number_delta=-2.0,
        confidence_score=0.992,
        status="completed",
        summary_report="Phase 484 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_484_Verification"
    assert study.decatenation_catalytic_rate_per_sec == 3.85

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Topoisomerase_G_Gate_Double_Strand_Passage",
        profile_category="Primary Step",
        quantitative_value=3.85,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Topoisomerase_G_Gate_Double_Strand_Passage"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="decatenation_catalytic_rate_per_sec",
        observed_value=3.85,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 3.85

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_484_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
