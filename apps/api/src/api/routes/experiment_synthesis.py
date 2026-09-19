"""API Routes for Autonomous AI Lab Co-Pilot & Centennial Synthesis Core (Phase 100)."""

import uuid
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.repositories.experiment_synthesis_repo import ExperimentSynthesisRepository
from research.automation.experiment_synthesis_engine import ExperimentSynthesisEngine

router = APIRouter(prefix="/experiment-synthesis", tags=["Autonomous Lab Co-Pilot & Centennial Synthesis"])


class ExperimentSynthesisRequest(BaseModel):
    campaign_title: str = Field(..., example="Autonomous De-Novo Kinase Inhibitor Discovery Campaign")
    scientific_domain: str = Field(default="Targeted Oncology & Chemical Biology", example="Targeted Oncology & Chemical Biology")
    hypothesis_statement: str = Field(
        ...,
        example="Small molecule dual-inhibition of CDK4/6 and PI3Kalpha yields synergistic senescence in Rb-proficient breast cancer cells.",
    )
    workspace_id: Optional[str] = None


@router.get("/pipeline-stages")
async def get_pipeline_stages():
    """Retrieve canonical 5-stage closed-loop autonomous research pipeline architecture."""
    return {"stages": ExperimentSynthesisEngine.PIPELINE_STAGES}


@router.post("/synthesize", status_code=status.HTTP_201_CREATED)
async def run_autonomous_experiment_synthesis(
    request: ExperimentSynthesisRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """Trigger end-to-end closed-loop autonomous experiment compilation from hypothesis to publication."""
    engine = ExperimentSynthesisEngine()
    result = engine.run_synthesis_campaign(
        campaign_title=request.campaign_title,
        scientific_domain=request.scientific_domain,
        hypothesis_statement=request.hypothesis_statement,
    )

    repo = ExperimentSynthesisRepository(db)
    ws_id = uuid.UUID(request.workspace_id) if request.workspace_id else uuid.uuid4()

    syn = await repo.create_synthesis(
        workspace_id=ws_id,
        campaign_title=result["campaign_title"],
        scientific_domain=result["scientific_domain"],
        hypothesis_statement=result["hypothesis_statement"],
        synthesis_summary=result["synthesis_summary"],
        autonomous_state=result["autonomous_state"],
        overall_confidence_score=result["overall_confidence_score"],
        total_pipeline_stages=result["total_pipeline_stages"],
        completed_stages_count=result["completed_stages_count"],
        synthesis_metadata={"engine_version": "v1.0-centennial"},
    )

    for st in result["action_steps"]:
        await repo.add_action_step(
            synthesis_id=syn.id,
            step_number=st["step_number"],
            stage_name=st["stage_name"],
            agent_persona=st["agent_persona"],
            output_summary=st["output_summary"],
            execution_status=st["execution_status"],
            latency_seconds=st["latency_seconds"],
        )

    for ver in result["verifications"]:
        await repo.add_verification(
            synthesis_id=syn.id,
            metric_name=ver["metric_name"],
            expected_value=ver["expected_value"],
            observed_value=ver["observed_value"],
            deviation_pct=ver["deviation_pct"],
            verification_passed=ver["verification_passed"],
        )

    return {
        "status": "SUCCESS",
        "synthesis_id": str(syn.id),
        "campaign_title": syn.campaign_title,
        "scientific_domain": syn.scientific_domain,
        "autonomous_state": syn.autonomous_state,
        "overall_confidence_score": syn.overall_confidence_score,
        "completed_stages_count": syn.completed_stages_count,
        "action_steps": result["action_steps"],
        "verifications": result["verifications"],
        "synthesis_summary": result["synthesis_summary"],
    }


@router.get("/campaigns/{synthesis_id}")
async def get_synthesis_campaign(
    synthesis_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """Retrieve full autonomous synthesis campaign details and telemetry traces."""
    repo = ExperimentSynthesisRepository(db)
    try:
        sid = uuid.UUID(synthesis_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid synthesis UUID format")

    syn = await repo.get_synthesis(sid)
    if not syn:
        raise HTTPException(status_code=404, detail="Synthesis campaign not found")

    return {
        "id": str(syn.id),
        "campaign_title": syn.campaign_title,
        "scientific_domain": syn.scientific_domain,
        "hypothesis_statement": syn.hypothesis_statement,
        "autonomous_state": syn.autonomous_state,
        "overall_confidence_score": syn.overall_confidence_score,
        "synthesis_summary": syn.synthesis_summary,
        "action_steps": [
            {
                "step_number": s.step_number,
                "stage_name": s.stage_name,
                "agent_persona": s.agent_persona,
                "output_summary": s.output_summary,
                "status": s.execution_status,
            }
            for s in syn.action_steps
        ],
        "verifications": [
            {
                "metric_name": v.metric_name,
                "expected_value": v.expected_value,
                "observed_value": v.observed_value,
                "passed": v.verification_passed,
            }
            for v in syn.verifications
        ],
    }
