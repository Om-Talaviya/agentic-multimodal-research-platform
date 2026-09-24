"""FastAPI Route for Milestone v1.8 Synthesis (Phase 154)."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.repositories.milestone_v1_8_repo import MilestoneV18Repository
from research.orchestration.milestone_v1_8_engine import (
    MilestoneV18SynthesisEngine,
    MilestoneV18SynthesisRequest,
    MilestoneV18SynthesisResult,
)

router = APIRouter(prefix="/milestone-v1-8", tags=["Milestone v1.8 Synthesis"])


@router.post("/synthesize", response_model=MilestoneV18SynthesisResult)
async def synthesize_milestone(
    payload: MilestoneV18SynthesisRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    engine = MilestoneV18SynthesisEngine()
    result = engine.synthesize(payload)

    repo = MilestoneV18Repository(db)
    orch = await repo.create_orchestration(
        orchestration_name=result.orchestration_name,
        milestone_version=result.milestone_version,
        total_phases_integrated=result.total_phases_integrated,
        cross_domain_pipeline_status=result.cross_domain_pipeline_status,
        orchestration_confidence_score=result.orchestration_confidence_score,
        global_system_entropy=result.global_system_entropy,
    )

    for n in result.workflow_nodes:
        await repo.add_workflow_node(
            orchestration_id=orch.id,
            node_name=n.node_name,
            domain_category=n.domain_category,
            phase_reference=n.phase_reference,
            execution_latency_ms=n.execution_latency_ms,
            node_fidelity_score=n.node_fidelity_score,
        )

    for r in result.executive_reports:
        await repo.add_executive_report(
            orchestration_id=orch.id,
            report_title=r.report_title,
            executive_summary=r.executive_summary,
            primary_breakthrough=r.primary_breakthrough,
            recommended_clinical_translation=r.recommended_clinical_translation,
        )

    return result
