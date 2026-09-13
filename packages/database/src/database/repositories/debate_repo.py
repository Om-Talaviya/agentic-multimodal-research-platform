"""Repository for Adversarial Multi-Agent Debate and Consensus persistence."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.debate import DBAgentDebate, DBDebateConsensus, DBDebateRound
from shared.logging import get_logger

logger = get_logger(__name__)


class DebateRepository:
    """Async repository for managing debate sessions, adversarial rounds, and consensus synthesis."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_debate(
        self,
        user_id: uuid.UUID,
        topic: str,
        initial_thesis: str,
        counter_thesis: Optional[str] = None,
        max_rounds: int = 3,
        proposer_model: str = "gemini-2.5-pro",
        opposer_model: str = "gemini-2.5-pro",
        arbiter_model: str = "gemini-2.5-pro",
        workspace_id: Optional[uuid.UUID] = None,
        project_id: Optional[uuid.UUID] = None,
        config_json: Optional[Dict[str, Any]] = None,
    ) -> DBAgentDebate:
        """Create a new multi-agent debate session."""
        debate = DBAgentDebate(
            id=uuid.uuid4(),
            user_id=user_id,
            workspace_id=workspace_id,
            project_id=project_id,
            topic=topic,
            initial_thesis=initial_thesis,
            counter_thesis=counter_thesis,
            status="active",
            max_rounds=max_rounds,
            current_round=0,
            proposer_model=proposer_model,
            opposer_model=opposer_model,
            arbiter_model=arbiter_model,
            proposer_elo=1500.0,
            opposer_elo=1500.0,
            config_json=config_json or {},
        )
        self.session.add(debate)
        await self.session.commit()
        await self.session.refresh(debate)
        logger.info("debate_created", debate_id=str(debate.id), topic=topic)
        return debate

    async def get_debate(
        self,
        debate_id: uuid.UUID,
        user_id: Optional[uuid.UUID] = None,
        include_rounds: bool = True,
        include_consensus: bool = True,
    ) -> Optional[DBAgentDebate]:
        """Fetch debate by ID with optional user validation and eager-loaded relations."""
        stmt = select(DBAgentDebate).where(DBAgentDebate.id == debate_id)
        if user_id:
            stmt = stmt.where(DBAgentDebate.user_id == user_id)

        if include_rounds:
            stmt = stmt.options(selectinload(DBAgentDebate.rounds))
        if include_consensus:
            stmt = stmt.options(selectinload(DBAgentDebate.consensus))

        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_debates(
        self,
        user_id: Optional[uuid.UUID] = None,
        workspace_id: Optional[uuid.UUID] = None,
        project_id: Optional[uuid.UUID] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[DBAgentDebate]:
        """Query debates with filtering options."""
        stmt = (
            select(DBAgentDebate)
            .options(
                selectinload(DBAgentDebate.rounds),
                selectinload(DBAgentDebate.consensus),
            )
            .order_by(DBAgentDebate.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        if user_id:
            stmt = stmt.where(DBAgentDebate.user_id == user_id)
        if workspace_id:
            stmt = stmt.where(DBAgentDebate.workspace_id == workspace_id)
        if project_id:
            stmt = stmt.where(DBAgentDebate.project_id == project_id)
        if status:
            stmt = stmt.where(DBAgentDebate.status == status)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_debate_status(
        self,
        debate_id: uuid.UUID,
        status: str,
        current_round: Optional[int] = None,
        proposer_elo: Optional[float] = None,
        opposer_elo: Optional[float] = None,
    ) -> Optional[DBAgentDebate]:
        """Update debate status and participant Elo ratings."""
        values: Dict[str, Any] = {
            "status": status,
            "updated_at": datetime.now(timezone.utc),
        }
        if current_round is not None:
            values["current_round"] = current_round
        if proposer_elo is not None:
            values["proposer_elo"] = proposer_elo
        if opposer_elo is not None:
            values["opposer_elo"] = opposer_elo

        stmt = (
            update(DBAgentDebate)
            .where(DBAgentDebate.id == debate_id)
            .values(**values)
            .execution_options(synchronize_session="fetch")
        )
        await self.session.execute(stmt)
        await self.session.commit()
        return await self.get_debate(debate_id)

    async def add_debate_round(
        self,
        debate_id: uuid.UUID,
        round_number: int,
        proposer_argument: str,
        opposer_argument: str,
        proposer_citations: Optional[List[Dict[str, Any]]] = None,
        opposer_citations: Optional[List[Dict[str, Any]]] = None,
        proposer_score: float = 0.0,
        opposer_score: float = 0.0,
        arbiter_critique: Optional[str] = None,
        round_winner: Optional[str] = None,
        elo_delta: float = 0.0,
        round_telemetry: Optional[Dict[str, Any]] = None,
    ) -> DBDebateRound:
        """Add a completed round to a debate session."""
        debate_round = DBDebateRound(
            id=uuid.uuid4(),
            debate_id=debate_id,
            round_number=round_number,
            proposer_argument=proposer_argument,
            proposer_citations=proposer_citations or [],
            proposer_score=proposer_score,
            opposer_argument=opposer_argument,
            opposer_citations=opposer_citations or [],
            opposer_score=opposer_score,
            arbiter_critique=arbiter_critique,
            round_winner=round_winner,
            elo_delta=elo_delta,
            round_telemetry=round_telemetry or {},
        )
        self.session.add(debate_round)
        await self.session.commit()
        await self.session.refresh(debate_round)
        logger.info(
            "debate_round_added",
            debate_id=str(debate_id),
            round_number=round_number,
            winner=round_winner,
        )
        return debate_round

    async def list_debate_rounds(self, debate_id: uuid.UUID) -> List[DBDebateRound]:
        """Fetch all chronological rounds for a given debate."""
        stmt = (
            select(DBDebateRound)
            .where(DBDebateRound.debate_id == debate_id)
            .order_by(DBDebateRound.round_number.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def record_consensus(
        self,
        debate_id: uuid.UUID,
        consensus_statement: str,
        accepted_claims: Optional[List[Dict[str, Any]]] = None,
        refuted_claims: Optional[List[Dict[str, Any]]] = None,
        concessions: Optional[List[Dict[str, Any]]] = None,
        remaining_uncertainties: Optional[List[str]] = None,
        overall_confidence: float = 0.0,
        winner_overall: str = "balanced_consensus",
        final_proposer_elo: float = 1500.0,
        final_opposer_elo: float = 1500.0,
        synthesis_metadata: Optional[Dict[str, Any]] = None,
    ) -> DBDebateConsensus:
        """Persist synthesized consensus for a concluded debate."""
        consensus = DBDebateConsensus(
            id=uuid.uuid4(),
            debate_id=debate_id,
            consensus_statement=consensus_statement,
            accepted_claims=accepted_claims or [],
            refuted_claims=refuted_claims or [],
            concessions=concessions or [],
            remaining_uncertainties=remaining_uncertainties or [],
            overall_confidence=overall_confidence,
            winner_overall=winner_overall,
            final_proposer_elo=final_proposer_elo,
            final_opposer_elo=final_opposer_elo,
            synthesis_metadata=synthesis_metadata or {},
        )
        self.session.add(consensus)
        await self.session.commit()
        await self.session.refresh(consensus)

        # Update debate status to concluded
        await self.update_debate_status(
            debate_id=debate_id,
            status="concluded",
            proposer_elo=final_proposer_elo,
            opposer_elo=final_opposer_elo,
        )
        logger.info(
            "debate_consensus_recorded",
            debate_id=str(debate_id),
            winner=winner_overall,
            confidence=overall_confidence,
        )
        return consensus

    async def get_consensus(
        self, debate_id: uuid.UUID
    ) -> Optional[DBDebateConsensus]:
        """Fetch consensus record for a debate."""
        stmt = select(DBDebateConsensus).where(DBDebateConsensus.debate_id == debate_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_debate_metrics(
        self,
        user_id: Optional[uuid.UUID] = None,
        workspace_id: Optional[uuid.UUID] = None,
    ) -> Dict[str, Any]:
        """Compute aggregate debate KPIs."""
        base_stmt = select(DBAgentDebate)
        if user_id:
            base_stmt = base_stmt.where(DBAgentDebate.user_id == user_id)
        if workspace_id:
            base_stmt = base_stmt.where(DBAgentDebate.workspace_id == workspace_id)

        all_debates = list((await self.session.execute(base_stmt)).scalars().all())
        total_debates = len(all_debates)
        active_debates = sum(1 for d in all_debates if d.status == "active")
        concluded_debates = sum(1 for d in all_debates if d.status == "concluded")

        # Consensus query
        consensus_stmt = select(DBDebateConsensus)
        all_consensus = list(
            (await self.session.execute(consensus_stmt)).scalars().all()
        )
        avg_confidence = (
            sum(c.overall_confidence for c in all_consensus) / len(all_consensus)
            if all_consensus
            else 0.0
        )

        return {
            "total_debates": total_debates,
            "active_debates": active_debates,
            "concluded_debates": concluded_debates,
            "mean_confidence": round(avg_confidence, 3),
            "proposer_avg_elo": round(
                sum(d.proposer_elo for d in all_debates) / total_debates
                if total_debates
                else 1500.0,
                1,
            ),
            "opposer_avg_elo": round(
                sum(d.opposer_elo for d in all_debates) / total_debates
                if total_debates
                else 1500.0,
                1,
            ),
        }

    async def delete_debate(self, debate_id: uuid.UUID) -> bool:
        """Permanently delete a debate and all associated rounds and consensus."""
        stmt = delete(DBAgentDebate).where(DBAgentDebate.id == debate_id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return bool(result.rowcount > 0)
