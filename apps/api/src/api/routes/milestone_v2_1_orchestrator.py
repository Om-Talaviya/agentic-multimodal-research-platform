"""FastAPI routes for Phase 187: Milestone v2.1 Planetary Meta-Orchestrator Studio."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.milestone_v2_1_orchestrator_repo import MilestoneV21OrchestratorRepository
from research.orchestration.milestone_v2_1_orchestrator_engine import MilestoneV21OrchestratorEngine

router = APIRouter(prefix="/milestone-v2-1", tags=["Milestone v2.1 Planetary Meta-Orchestrator"])


class RunPlanetarySynthesisRequest(BaseModel):
    name: str = Field(..., example="Planetary Research Meta-Synthesis 2026")
    mission_scope: str = Field(default="Planetary Multimodal Autonomous Synthesis")
    active_subsystems_count: int = Field(default=187, ge=1, le=500)
    global_cross_correlation_input: float = Field(default=0.982, ge=0.0, le=1.0)


@router.post("/synthesize", status_code=status.HTTP_201_CREATED)
async def synthesize_and_persist_milestone(
    req: RunPlanetarySynthesisRequest,
    session: AsyncSession = Depends(get_db_session),
):
    engine = MilestoneV21OrchestratorEngine()
    result = engine.run_planetary_synthesis(
        mission_scope=req.mission_scope,
        active_subsystems_count=req.active_subsystems_count,
        global_cross_correlation_input=req.global_cross_correlation_input,
    )

    repo = MilestoneV21OrchestratorRepository(session)
    study = await repo.create_study(
        name=req.name,
        mission_scope=result.mission_scope,
        active_subsystems_count=result.active_subsystems_count,
        global_cross_correlation_index=result.global_cross_correlation_index,
        synthesis_confidence_score=result.synthesis_confidence_score,
        autonomous_discovery_throughput=result.autonomous_discovery_throughput,
        status="completed",
        orchestration_parameters={
            "orchestration_health_score": result.orchestration_health_score,
        },
        executive_synthesis_report=result.executive_synthesis_report,
    )

    for t in result.telemetries:
        await repo.add_telemetry(
            study_id=study.id,
            subsystem_domain=t.subsystem_domain,
            subsystem_phase_code=t.subsystem_phase_code,
            throughput_ops_sec=t.throughput_ops_sec,
            cross_validation_accuracy=t.cross_validation_accuracy,
            latency_ms=t.latency_ms,
        )

    for r in result.planetary_runs:
        await repo.add_planetary_run(
            study_id=study.id,
            run_identifier=r.run_identifier,
            generated_hypotheses=r.generated_hypotheses,
            validated_lead_targets=r.validated_lead_targets,
            meta_synthesis_entropy=r.meta_synthesis_entropy,
        )

    return {
        "id": str(study.id),
        "name": study.name,
        "mission_scope": study.mission_scope,
        "active_subsystems_count": study.active_subsystems_count,
        "global_cross_correlation_index": study.global_cross_correlation_index,
        "synthesis_confidence_score": study.synthesis_confidence_score,
        "autonomous_discovery_throughput": study.autonomous_discovery_throughput,
        "telemetries": [
            {
                "subsystem_domain": t.subsystem_domain,
                "subsystem_phase_code": t.subsystem_phase_code,
                "throughput_ops_sec": t.throughput_ops_sec,
                "cross_validation_accuracy": t.cross_validation_accuracy,
                "latency_ms": t.latency_ms,
            }
            for t in result.telemetries
        ],
        "planetary_runs": [
            {
                "run_identifier": r.run_identifier,
                "generated_hypotheses": r.generated_hypotheses,
                "validated_lead_targets": r.validated_lead_targets,
                "meta_synthesis_entropy": r.meta_synthesis_entropy,
            }
            for r in result.planetary_runs
        ],
        "executive_synthesis_report": study.executive_synthesis_report,
    }


@router.get("/studies")
async def list_milestone_studies(
    limit: int = Query(50, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    repo = MilestoneV21OrchestratorRepository(session)
    studies = await repo.list_studies(limit=limit)
    return [
        {
            "id": str(s.id),
            "name": s.name,
            "mission_scope": s.mission_scope,
            "active_subsystems_count": s.active_subsystems_count,
            "global_cross_correlation_index": s.global_cross_correlation_index,
            "synthesis_confidence_score": s.synthesis_confidence_score,
            "autonomous_discovery_throughput": s.autonomous_discovery_throughput,
            "status": s.status,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in studies
    ]
