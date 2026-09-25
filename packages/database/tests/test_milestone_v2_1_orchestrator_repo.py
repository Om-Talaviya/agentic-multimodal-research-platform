"""Tests for Phase 187: Milestone v2.1 Database Repository."""

import pytest
from database.repositories.milestone_v2_1_orchestrator_repo import MilestoneV21OrchestratorRepository


@pytest.mark.asyncio
async def test_milestone_v2_1_orchestrator_repository(db_session):
    repo = MilestoneV21OrchestratorRepository(db_session)

    study = await repo.create_study(
        name="Global Autonomous Milestone v2.1",
        mission_scope="Planetary Multimodal Autonomous Synthesis",
        active_subsystems_count=187,
        global_cross_correlation_index=0.985,
        synthesis_confidence_score=0.995,
        autonomous_discovery_throughput=425.0,
        status="completed",
        executive_synthesis_report="Global cross-omics and structural systems validated.",
    )
    assert study.id is not None
    assert study.name == "Global Autonomous Milestone v2.1"
    assert study.active_subsystems_count == 187

    telemetry = await repo.add_telemetry(
        study_id=study.id,
        subsystem_domain="Multi-Parametric Oncology Radiomics",
        subsystem_phase_code="Phase 186",
        throughput_ops_sec=820.0,
        cross_validation_accuracy=0.985,
        latency_ms=18.5,
    )
    assert telemetry.id is not None
    assert telemetry.subsystem_domain == "Multi-Parametric Oncology Radiomics"

    run = await repo.add_planetary_run(
        study_id=study.id,
        run_identifier="PLN-SYNTH-2026-ALPHA",
        generated_hypotheses=1500,
        validated_lead_targets=95,
        meta_synthesis_entropy=0.125,
    )
    assert run.id is not None
    assert run.generated_hypotheses == 1500

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.name == "Global Autonomous Milestone v2.1"

    all_studies = await repo.list_studies(limit=10)
    assert len(all_studies) >= 1
