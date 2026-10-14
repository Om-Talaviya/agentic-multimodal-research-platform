"""Tests for Phase 513: Autonomous Cross-Species Synthetic Quorum Sensing Interbacterial Commensal Switch Modeler Repo."""

import pytest
from database.repositories.synthetic_quorum_sensing_cross_species_switch_repo import SyntheticQuorumSensingCrossSpeciesSwitchRepository


@pytest.mark.asyncio
async def test_synthetic_quorum_sensing_cross_species_switch_repository(db_session):
    repo = SyntheticQuorumSensingCrossSpeciesSwitchRepository(db_session)

    study = await repo.create_study(
        name="Study_513_Verification",
        target_specimen="Co-Cultured Synthetic E. coli and B. subtilis Biofilm with AI-2 / CAI-1 Inter-Species Relays",
        analytical_modality="cross-species-quorum-switch",
        interbacterial_signal_induction_threshold_nM=85.0,
        population_ratio_homeostasis_cv=0.042,
        cross_repression_bistable_switch_delay_min=18.5,
        metabolic_cross_feeding_syntrophy_rate_mM_per_hr=3.2,
        confidence_score=0.99,
        status="completed",
        summary_report="Phase 513 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_513_Verification"
    assert study.interbacterial_signal_induction_threshold_nM == 85.0

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Interspecies_AI2_Relay_Transcriptional_Lock",
        profile_category="Primary Step",
        quantitative_value=85.0,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Interspecies_AI2_Relay_Transcriptional_Lock"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="interbacterial_signal_induction_threshold_nM",
        observed_value=85.0,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 85.0

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_513_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
