"""REST API endpoints for Adversarial Multi-Agent Debates and Consensus Synthesis."""

from typing import Any, Dict, List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from agents.base import AgentContext
from api.dependencies import get_current_user, get_db_session, get_model_gateway
from ai.gateway import ModelGateway
from database.models.user import User
from database.repositories.debate_repo import DebateRepository
from research.debate.engine import DebateEngine
from shared.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/debates", tags=["Debates"])


class CreateDebatePayload(BaseModel):
    """Payload for creating a new multi-agent debate session."""

    topic: str = Field(..., min_length=3, max_length=500)
    initial_thesis: str = Field(..., min_length=5)
    counter_thesis: Optional[str] = None
    max_rounds: int = Field(default=3, ge=1, le=10)
    proposer_model: str = "gemini-2.5-pro"
    opposer_model: str = "gemini-2.5-pro"
    arbiter_model: str = "gemini-2.5-pro"
    workspace_id: Optional[uuid.UUID] = None
    project_id: Optional[uuid.UUID] = None
    config_json: Optional[Dict[str, Any]] = None


class ExecuteRoundPayload(BaseModel):
    """Payload for executing a debate round."""

    run_to_completion: bool = Field(default=False)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_debate(
    payload: CreateDebatePayload,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Launch a new adversarial multi-agent debate session."""
    repo = DebateRepository(session)
    debate = await repo.create_debate(
        user_id=current_user.id,
        topic=payload.topic,
        initial_thesis=payload.initial_thesis,
        counter_thesis=payload.counter_thesis,
        max_rounds=payload.max_rounds,
        proposer_model=payload.proposer_model,
        opposer_model=payload.opposer_model,
        arbiter_model=payload.arbiter_model,
        workspace_id=payload.workspace_id,
        project_id=payload.project_id,
        config_json=payload.config_json,
    )
    return {
        "id": str(debate.id),
        "topic": debate.topic,
        "initial_thesis": debate.initial_thesis,
        "counter_thesis": debate.counter_thesis,
        "status": debate.status,
        "max_rounds": debate.max_rounds,
        "current_round": debate.current_round,
        "proposer_elo": debate.proposer_elo,
        "opposer_elo": debate.opposer_elo,
        "created_at": debate.created_at.isoformat(),
    }


@router.get("")
async def list_debates(
    workspace_id: Optional[uuid.UUID] = Query(None),
    project_id: Optional[uuid.UUID] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> List[Dict[str, Any]]:
    """List adversarial debates with filtering."""
    repo = DebateRepository(session)
    debates = await repo.list_debates(
        user_id=current_user.id if not workspace_id else None,
        workspace_id=workspace_id,
        project_id=project_id,
        status=status_filter,
        limit=limit,
        offset=offset,
    )
    return [
        {
            "id": str(d.id),
            "topic": d.topic,
            "initial_thesis": d.initial_thesis,
            "counter_thesis": d.counter_thesis,
            "status": d.status,
            "max_rounds": d.max_rounds,
            "current_round": d.current_round,
            "proposer_elo": d.proposer_elo,
            "opposer_elo": d.opposer_elo,
            "rounds_count": len(d.rounds or []),
            "has_consensus": d.consensus is not None,
            "created_at": d.created_at.isoformat(),
        }
        for d in debates
    ]


@router.get("/metrics")
async def get_debate_metrics(
    workspace_id: Optional[uuid.UUID] = Query(None),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Get aggregate debate and Elo metrics."""
    repo = DebateRepository(session)
    return await repo.get_debate_metrics(
        user_id=current_user.id if not workspace_id else None,
        workspace_id=workspace_id,
    )


@router.get("/{debate_id}")
async def get_debate(
    debate_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Retrieve full details of a debate session."""
    repo = DebateRepository(session)
    debate = await repo.get_debate(debate_id)
    if not debate:
        raise HTTPException(status_code=404, detail="Debate not found")

    consensus_dict = None
    if debate.consensus:
        c = debate.consensus
        consensus_dict = {
            "id": str(c.id),
            "consensus_statement": c.consensus_statement,
            "accepted_claims": c.accepted_claims,
            "refuted_claims": c.refuted_claims,
            "concessions": c.concessions,
            "remaining_uncertainties": c.remaining_uncertainties,
            "overall_confidence": c.overall_confidence,
            "winner_overall": c.winner_overall,
            "created_at": c.created_at.isoformat(),
        }

    return {
        "id": str(debate.id),
        "topic": debate.topic,
        "initial_thesis": debate.initial_thesis,
        "counter_thesis": debate.counter_thesis,
        "status": debate.status,
        "max_rounds": debate.max_rounds,
        "current_round": debate.current_round,
        "proposer_model": debate.proposer_model,
        "opposer_model": debate.opposer_model,
        "arbiter_model": debate.arbiter_model,
        "proposer_elo": debate.proposer_elo,
        "opposer_elo": debate.opposer_elo,
        "rounds": [
            {
                "id": str(r.id),
                "round_number": r.round_number,
                "proposer_argument": r.proposer_argument,
                "opposer_argument": r.opposer_argument,
                "proposer_citations": r.proposer_citations,
                "opposer_citations": r.opposer_citations,
                "proposer_score": r.proposer_score,
                "opposer_score": r.opposer_score,
                "arbiter_critique": r.arbiter_critique,
                "round_winner": r.round_winner,
                "elo_delta": r.elo_delta,
                "created_at": r.created_at.isoformat(),
            }
            for r in (debate.rounds or [])
        ],
        "consensus": consensus_dict,
        "created_at": debate.created_at.isoformat(),
    }


@router.post("/{debate_id}/rounds")
async def execute_debate_round(
    debate_id: uuid.UUID,
    payload: ExecuteRoundPayload = ExecuteRoundPayload(),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    gateway: Optional[ModelGateway] = Depends(get_model_gateway),
) -> Dict[str, Any]:
    """Execute the next round or complete the remaining rounds of a debate."""
    repo = DebateRepository(session)
    debate = await repo.get_debate(debate_id)
    if not debate:
        raise HTTPException(status_code=404, detail="Debate not found")

    if debate.status != "active":
        raise HTTPException(status_code=400, detail=f"Debate is already {debate.status}")

    context = AgentContext(
        user_id=current_user.id,
        workspace_id=debate.workspace_id,
        project_id=debate.project_id,
        model_gateway=gateway,
    )
    engine = DebateEngine(debate_repo=repo)

    if payload.run_to_completion:
        result = await engine.execute_full_debate(debate_id, context)
    else:
        result = await engine.execute_round(debate_id, context)

    return result


@router.get("/{debate_id}/rounds")
async def list_rounds(
    debate_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> List[Dict[str, Any]]:
    """List chronological rounds of a debate."""
    repo = DebateRepository(session)
    rounds = await repo.list_debate_rounds(debate_id)
    return [
        {
            "id": str(r.id),
            "round_number": r.round_number,
            "proposer_argument": r.proposer_argument,
            "opposer_argument": r.opposer_argument,
            "proposer_citations": r.proposer_citations,
            "opposer_citations": r.opposer_citations,
            "proposer_score": r.proposer_score,
            "opposer_score": r.opposer_score,
            "arbiter_critique": r.arbiter_critique,
            "round_winner": r.round_winner,
            "elo_delta": r.elo_delta,
            "created_at": r.created_at.isoformat(),
        }
        for r in rounds
    ]


@router.get("/{debate_id}/consensus")
async def get_debate_consensus(
    debate_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Retrieve synthesized consensus for a debate."""
    repo = DebateRepository(session)
    consensus = await repo.get_consensus(debate_id)
    if not consensus:
        raise HTTPException(status_code=404, detail="Consensus not yet synthesized")

    return {
        "id": str(consensus.id),
        "debate_id": str(consensus.debate_id),
        "consensus_statement": consensus.consensus_statement,
        "accepted_claims": consensus.accepted_claims,
        "refuted_claims": consensus.refuted_claims,
        "concessions": consensus.concessions,
        "remaining_uncertainties": consensus.remaining_uncertainties,
        "overall_confidence": consensus.overall_confidence,
        "winner_overall": consensus.winner_overall,
        "final_proposer_elo": consensus.final_proposer_elo,
        "final_opposer_elo": consensus.final_opposer_elo,
        "created_at": consensus.created_at.isoformat(),
    }


@router.delete("/{debate_id}")
async def delete_debate(
    debate_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Delete a debate session and all child records."""
    repo = DebateRepository(session)
    success = await repo.delete_debate(debate_id)
    if not success:
        raise HTTPException(status_code=404, detail="Debate not found")
    return {"deleted": True, "debate_id": str(debate_id)}
