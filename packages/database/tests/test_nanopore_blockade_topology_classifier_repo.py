"""Tests for Phase 450: Autonomous Nanopore Ionic Current Blockade Shape Classifier for Macromolecular Topologies Repo."""

import pytest
from database.repositories.nanopore_blockade_topology_classifier_repo import NanoporeBlockadeTopologyRepository


@pytest.mark.asyncio
async def test_nanopore_blockade_topology_classifier_repository(db_session):
    repo = NanoporeBlockadeTopologyRepository(db_session)

    study = await repo.create_study(
        name="Study_450_Verification",
        target_specimen="Supercoiled Plasmid DNA and Knotted Circular Peptides Passing Through 4nm Aerolysin Pore",
        analytical_modality="nanopore-blockade-topology",
        dwell_time_topological_knot_us=84.5,
        fractional_blockade_current_depth_ratio=0.892,
        topology_classification_accuracy=0.978,
        translocation_velocity_nt_per_ms=4.2,
        confidence_score=0.992,
        status="completed",
        summary_report="Phase 450 automated test run.",
    )
    assert study.id is not None
    assert study.name == "Study_450_Verification"
    assert study.dwell_time_topological_knot_us == 84.5

    item = await repo.add_item_profile(
        study_id=study.id,
        item_name="Multi_State_Ionic_Current_Blockade_Signal",
        profile_category="Primary Step",
        quantitative_value=84.5,
        log2_fold_change=-2.45,
        significance_score=0.998,
    )
    assert item.id is not None
    assert item.item_name == "Multi_State_Ionic_Current_Blockade_Signal"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="dwell_time_topological_knot_us",
        observed_value=84.5,
        z_score=-3.42,
        p_value=0.0001,
    )
    assert trace.id is not None
    assert trace.observed_value == 84.5

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Study_450_Verification"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
