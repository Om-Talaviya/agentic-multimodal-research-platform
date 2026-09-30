"""Tests for Phase 408: Autonomous Multi-State smFRET Hidden Markov Model Kinetic Rate Matrix Extractor Repo."""

import pytest
from database.repositories.single_molecule_fret_kinetics_repo import SingleMoleculeFretKineticsRepository


@pytest.mark.asyncio
async def test_single_molecule_fret_kinetics_repository(db_session):
    repo = SingleMoleculeFretKineticsRepository(db_session)

    study = await repo.create_study(
        name="Study_408_Verification",
        target_specimen="Human Patient Cohort Sample",
        analytical_modality="single-molecule-fret-kinetics",
        fret_efficiency_state_transition_rate_per_sec=38.6,
        viterbi_hidden_state_assignment_accuracy_pct=98.9,
        confidence_score=0.985,
        status="completed",
        summary_report="Phase 408 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_408_Verification"
    assert getattr(study, "fret_efficiency_state_transition_rate_per_sec") == 38.6

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Cy3_Donor_Cy5_Acceptor_Photobleaching_Dwell_Time_Trace",
        profile_category="Primary Target",
        quantitative_value=452.8,
        log2_fold_change=3.45,
        significance_score=0.992,
    )
    assert item.id is not None
    assert item.item_name == "Cy3_Donor_Cy5_Acceptor_Photobleaching_Dwell_Time_Trace"

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
    assert fetched.name == "Study_408_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
