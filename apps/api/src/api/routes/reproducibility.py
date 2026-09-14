"""REST API endpoints for In-Silico Experimentation, Computational Reproducibility, and Claim Verification."""

from typing import Any, Dict, List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user, get_db_session
from database.models.user import User
from database.repositories.reproducibility_repo import ReproducibilityRepository
from research.reproducibility.engine import ReproducibilityEngine
from shared.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/reproducibility", tags=["Reproducibility & Experimentation"])


# ---------------- Schemas ----------------

class CreateProtocolPayload(BaseModel):
    name: str = Field(..., min_length=3, max_length=300)
    executable_code: str = Field(..., min_length=5)
    description: Optional[str] = None
    source_paper_title: Optional[str] = None
    source_doi: Optional[str] = None
    runtime_language: str = Field(default="python3")
    parameters: Optional[Dict[str, Any]] = None
    dependencies: Optional[List[str]] = None
    claimed_metrics: Optional[Dict[str, float]] = None
    workspace_id: Optional[uuid.UUID] = None
    project_id: Optional[uuid.UUID] = None


class ExecuteProtocolPayload(BaseModel):
    override_parameters: Optional[Dict[str, Any]] = None
    tolerance_threshold: float = Field(default=0.05, ge=0.001, le=0.50)


# ---------------- Protocol Endpoints ----------------

@router.post("/protocols", status_code=status.HTTP_201_CREATED)
async def create_protocol(
    payload: CreateProtocolPayload,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Register a new computational experiment protocol."""
    repo = ReproducibilityRepository(session)
    protocol = await repo.create_protocol(
        user_id=current_user.id,
        name=payload.name,
        executable_code=payload.executable_code,
        description=payload.description,
        source_paper_title=payload.source_paper_title,
        source_doi=payload.source_doi,
        runtime_language=payload.runtime_language,
        parameters=payload.parameters,
        dependencies=payload.dependencies,
        claimed_metrics=payload.claimed_metrics,
        workspace_id=payload.workspace_id,
        project_id=payload.project_id,
    )
    return {
        "id": str(protocol.id),
        "name": protocol.name,
        "description": protocol.description,
        "source_paper_title": protocol.source_paper_title,
        "runtime_language": protocol.runtime_language,
        "parameters": protocol.parameters,
        "claimed_metrics": protocol.claimed_metrics,
        "verification_status": protocol.verification_status,
        "created_at": protocol.created_at.isoformat(),
    }


@router.get("/protocols")
async def list_protocols(
    workspace_id: Optional[uuid.UUID] = Query(None),
    project_id: Optional[uuid.UUID] = Query(None),
    verification_status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> List[Dict[str, Any]]:
    """List experiment protocols with optional filtering."""
    repo = ReproducibilityRepository(session)
    protocols = await repo.list_protocols(
        user_id=current_user.id if not workspace_id else None,
        workspace_id=workspace_id,
        project_id=project_id,
        verification_status=verification_status,
        limit=limit,
        offset=offset,
    )
    return [
        {
            "id": str(p.id),
            "name": p.name,
            "description": p.description,
            "source_paper_title": p.source_paper_title,
            "runtime_language": p.runtime_language,
            "verification_status": p.verification_status,
            "claimed_metrics": p.claimed_metrics,
            "total_runs": len(p.runs),
            "created_at": p.created_at.isoformat(),
        }
        for p in protocols
    ]


@router.get("/protocols/{protocol_id}")
async def get_protocol(
    protocol_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Fetch complete protocol details including historical runs and claim verification traces."""
    repo = ReproducibilityRepository(session)
    protocol = await repo.get_protocol(protocol_id)
    if not protocol:
        raise HTTPException(status_code=404, detail="Experiment protocol not found")

    return {
        "id": str(protocol.id),
        "name": protocol.name,
        "description": protocol.description,
        "source_paper_title": protocol.source_paper_title,
        "source_doi": protocol.source_doi,
        "runtime_language": protocol.runtime_language,
        "executable_code": protocol.executable_code,
        "parameters": protocol.parameters,
        "dependencies": protocol.dependencies,
        "claimed_metrics": protocol.claimed_metrics,
        "verification_status": protocol.verification_status,
        "created_at": protocol.created_at.isoformat(),
        "runs": [
            {
                "id": str(r.id),
                "status": r.status,
                "execution_time_ms": r.execution_time_ms,
                "memory_peak_mb": r.memory_peak_mb,
                "reproduced_metrics": r.reproduced_metrics,
                "reproducibility_score": r.reproducibility_score,
                "runtime_logs": r.runtime_logs,
                "error_message": r.error_message,
                "created_at": r.created_at.isoformat(),
            }
            for r in protocol.runs
        ],
        "verification_traces": [
            {
                "id": str(t.id),
                "run_id": str(t.run_id),
                "claim_statement": t.claim_statement,
                "metric_name": t.metric_name,
                "claimed_value": t.claimed_value,
                "reproduced_value": t.reproduced_value,
                "delta_relative_error": t.delta_relative_error,
                "verdict": t.verdict,
                "analysis_notes": t.analysis_notes,
                "created_at": t.created_at.isoformat(),
            }
            for t in protocol.verification_traces
        ],
    }


@router.post("/protocols/{protocol_id}/execute", status_code=status.HTTP_201_CREATED)
async def execute_protocol(
    protocol_id: uuid.UUID,
    payload: ExecuteProtocolPayload,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Execute protocol in sandbox, verify empirical claims, and record trace metrics."""
    repo = ReproducibilityRepository(session)
    protocol = await repo.get_protocol(protocol_id)
    if not protocol:
        raise HTTPException(status_code=404, detail="Experiment protocol not found")

    # Merge default parameters with overrides
    params = dict(protocol.parameters or {})
    if payload.override_parameters:
        params.update(payload.override_parameters)

    # Execute in sandbox
    exec_result = ReproducibilityEngine.execute_protocol(
        code_str=protocol.executable_code,
        parameters=params,
    )

    # Verify claims
    verification = ReproducibilityEngine.verify_claims(
        claimed_metrics=protocol.claimed_metrics or {},
        reproduced_metrics=exec_result["reproduced_metrics"],
        default_tolerance=payload.tolerance_threshold,
    )

    # Persist Run
    run = await repo.record_reproducibility_run(
        protocol_id=protocol.id,
        executed_by=current_user.id,
        status=exec_result["status"],
        execution_time_ms=exec_result["execution_time_ms"],
        memory_peak_mb=exec_result["memory_peak_mb"],
        reproduced_metrics=exec_result["reproduced_metrics"],
        reproducibility_score=verification["reproducibility_score"],
        runtime_logs=exec_result["runtime_logs"],
        error_message=exec_result["error_message"],
    )

    # Persist Individual Claim Verification Traces
    saved_traces = []
    for trace in verification["traces"]:
        t = await repo.record_verification_trace(
            protocol_id=protocol.id,
            run_id=run.id,
            claim_statement=trace["claim_statement"],
            metric_name=trace["metric_name"],
            claimed_value=trace["claimed_value"],
            reproduced_value=trace["reproduced_value"],
            delta_relative_error=trace["delta_relative_error"],
            verdict=trace["verdict"],
            tolerance_threshold=trace["tolerance_threshold"],
            analysis_notes=trace["analysis_notes"],
        )
        saved_traces.append(t)

    # Update Protocol Status
    await repo.update_protocol_status(protocol.id, verification["overall_status"])

    return {
        "run_id": str(run.id),
        "protocol_id": str(protocol.id),
        "status": run.status,
        "execution_time_ms": run.execution_time_ms,
        "reproduced_metrics": run.reproduced_metrics,
        "reproducibility_score": run.reproducibility_score,
        "overall_status": verification["overall_status"],
        "runtime_logs": run.runtime_logs,
        "error_message": run.error_message,
        "traces": [
            {
                "id": str(t.id),
                "metric_name": t.metric_name,
                "claimed_value": t.claimed_value,
                "reproduced_value": t.reproduced_value,
                "delta_relative_error": t.delta_relative_error,
                "verdict": t.verdict,
            }
            for t in saved_traces
        ],
    }


@router.delete("/protocols/{protocol_id}", status_code=status.HTTP_200_OK)
async def delete_protocol(
    protocol_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Delete an experiment protocol and cascade historical runs."""
    repo = ReproducibilityRepository(session)
    deleted = await repo.delete_protocol(protocol_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Experiment protocol not found")
    return {"message": "Experiment protocol deleted", "id": str(protocol_id)}


@router.get("/metrics")
async def get_reproducibility_platform_metrics(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Query aggregate reproducibility platform metrics."""
    repo = ReproducibilityRepository(session)
    return await repo.get_reproducibility_metrics()
