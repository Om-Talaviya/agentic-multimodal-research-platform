"""Repository for In-Silico Experimentation, Reproducibility Runs, and Claim Verification persistence."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.reproducibility import (
    DBClaimVerificationTrace,
    DBExperimentProtocol,
    DBReproducibilityRun,
)
from shared.logging import get_logger

logger = get_logger(__name__)


class ReproducibilityRepository:
    """Async repository for managing computational experiment protocols, execution runs, and claim verification."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_protocol(
        self,
        user_id: uuid.UUID,
        name: str,
        executable_code: str,
        description: Optional[str] = None,
        source_paper_title: Optional[str] = None,
        source_doi: Optional[str] = None,
        runtime_language: str = "python3",
        parameters: Optional[Dict[str, Any]] = None,
        dependencies: Optional[List[str]] = None,
        claimed_metrics: Optional[Dict[str, Any]] = None,
        workspace_id: Optional[uuid.UUID] = None,
        project_id: Optional[uuid.UUID] = None,
    ) -> DBExperimentProtocol:
        """Register a computational protocol."""
        protocol = DBExperimentProtocol(
            id=uuid.uuid4(),
            user_id=user_id,
            workspace_id=workspace_id,
            project_id=project_id,
            name=name,
            description=description,
            source_paper_title=source_paper_title,
            source_doi=source_doi,
            runtime_language=runtime_language,
            executable_code=executable_code,
            parameters=parameters or {},
            dependencies=dependencies or ["math"],
            claimed_metrics=claimed_metrics or {},
            verification_status="unverified",
        )
        self.session.add(protocol)
        await self.session.commit()
        await self.session.refresh(protocol)
        logger.info("experiment_protocol_created", protocol_id=str(protocol.id), name=name)
        return protocol

    async def get_protocol(
        self,
        protocol_id: uuid.UUID,
        user_id: Optional[uuid.UUID] = None,
        include_runs: bool = True,
        include_traces: bool = True,
    ) -> Optional[DBExperimentProtocol]:
        """Fetch an experiment protocol with eager runs and verification traces."""
        stmt = select(DBExperimentProtocol).where(DBExperimentProtocol.id == protocol_id)
        if user_id:
            stmt = stmt.where(DBExperimentProtocol.user_id == user_id)

        if include_runs:
            stmt = stmt.options(selectinload(DBExperimentProtocol.runs))
        if include_traces:
            stmt = stmt.options(selectinload(DBExperimentProtocol.verification_traces))

        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_protocols(
        self,
        user_id: Optional[uuid.UUID] = None,
        workspace_id: Optional[uuid.UUID] = None,
        project_id: Optional[uuid.UUID] = None,
        verification_status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[DBExperimentProtocol]:
        """Query experiment protocols with filtering."""
        stmt = (
            select(DBExperimentProtocol)
            .options(
                selectinload(DBExperimentProtocol.runs),
                selectinload(DBExperimentProtocol.verification_traces),
            )
            .order_by(DBExperimentProtocol.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        if user_id:
            stmt = stmt.where(DBExperimentProtocol.user_id == user_id)
        if workspace_id:
            stmt = stmt.where(DBExperimentProtocol.workspace_id == workspace_id)
        if project_id:
            stmt = stmt.where(DBExperimentProtocol.project_id == project_id)
        if verification_status:
            stmt = stmt.where(DBExperimentProtocol.verification_status == verification_status)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_protocol_status(
        self,
        protocol_id: uuid.UUID,
        verification_status: str,
    ) -> Optional[DBExperimentProtocol]:
        """Update protocol verification status."""
        stmt = (
            update(DBExperimentProtocol)
            .where(DBExperimentProtocol.id == protocol_id)
            .values(verification_status=verification_status, updated_at=datetime.now(timezone.utc))
            .returning(DBExperimentProtocol)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalars().first()

    async def delete_protocol(self, protocol_id: uuid.UUID) -> bool:
        """Delete an experiment protocol and cascade runs and traces."""
        stmt = delete(DBExperimentProtocol).where(DBExperimentProtocol.id == protocol_id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return (result.rowcount or 0) > 0

    # ---------------- Reproducibility Run Operations ----------------

    async def record_reproducibility_run(
        self,
        protocol_id: uuid.UUID,
        executed_by: uuid.UUID,
        status: str,
        execution_time_ms: float,
        memory_peak_mb: float,
        reproduced_metrics: Dict[str, Any],
        reproducibility_score: float,
        runtime_logs: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> DBReproducibilityRun:
        """Record an in-silico execution run."""
        run = DBReproducibilityRun(
            id=uuid.uuid4(),
            protocol_id=protocol_id,
            executed_by=executed_by,
            status=status,
            execution_time_ms=execution_time_ms,
            memory_peak_mb=memory_peak_mb,
            reproduced_metrics=reproduced_metrics,
            reproducibility_score=reproducibility_score,
            runtime_logs=runtime_logs,
            error_message=error_message,
        )
        self.session.add(run)
        await self.session.commit()
        await self.session.refresh(run)
        return run

    async def get_run(self, run_id: uuid.UUID) -> Optional[DBReproducibilityRun]:
        """Fetch run by ID."""
        stmt = select(DBReproducibilityRun).where(DBReproducibilityRun.id == run_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_runs(
        self,
        protocol_id: Optional[uuid.UUID] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[DBReproducibilityRun]:
        """List execution runs."""
        stmt = select(DBReproducibilityRun).order_by(DBReproducibilityRun.created_at.desc()).limit(limit).offset(offset)
        if protocol_id:
            stmt = stmt.where(DBReproducibilityRun.protocol_id == protocol_id)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # ---------------- Claim Verification Trace Operations ----------------

    async def record_verification_trace(
        self,
        protocol_id: uuid.UUID,
        run_id: uuid.UUID,
        claim_statement: str,
        metric_name: str,
        claimed_value: float,
        reproduced_value: float,
        delta_relative_error: float,
        verdict: str,
        tolerance_threshold: float = 0.05,
        analysis_notes: Optional[str] = None,
    ) -> DBClaimVerificationTrace:
        """Record a granular claim verification trace."""
        trace = DBClaimVerificationTrace(
            id=uuid.uuid4(),
            protocol_id=protocol_id,
            run_id=run_id,
            claim_statement=claim_statement,
            metric_name=metric_name,
            claimed_value=claimed_value,
            reproduced_value=reproduced_value,
            delta_relative_error=delta_relative_error,
            tolerance_threshold=tolerance_threshold,
            verdict=verdict,
            analysis_notes=analysis_notes,
        )
        self.session.add(trace)
        await self.session.commit()
        await self.session.refresh(trace)
        return trace

    async def list_verification_traces(
        self,
        protocol_id: Optional[uuid.UUID] = None,
        run_id: Optional[uuid.UUID] = None,
    ) -> List[DBClaimVerificationTrace]:
        """Query claim verification traces."""
        stmt = select(DBClaimVerificationTrace).order_by(DBClaimVerificationTrace.created_at.desc())
        if protocol_id:
            stmt = stmt.where(DBClaimVerificationTrace.protocol_id == protocol_id)
        if run_id:
            stmt = stmt.where(DBClaimVerificationTrace.run_id == run_id)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # ---------------- Aggregate Telemetry ----------------

    async def get_reproducibility_metrics(self) -> Dict[str, Any]:
        """Compute platform-wide computational reproducibility KPIs."""
        total_protocols = await self.session.scalar(select(func.count(DBExperimentProtocol.id))) or 0
        total_runs = await self.session.scalar(select(func.count(DBReproducibilityRun.id))) or 0
        succeeded_runs = await self.session.scalar(
            select(func.count(DBReproducibilityRun.id)).where(DBReproducibilityRun.status == "succeeded")
        ) or 0
        total_claims = await self.session.scalar(select(func.count(DBClaimVerificationTrace.id))) or 0
        reproduced_claims = await self.session.scalar(
            select(func.count(DBClaimVerificationTrace.id)).where(DBClaimVerificationTrace.verdict == "reproduced")
        ) or 0
        avg_score = await self.session.scalar(select(func.avg(DBReproducibilityRun.reproducibility_score))) or 0.0

        return {
            "total_protocols": total_protocols,
            "total_runs": total_runs,
            "succeeded_runs": succeeded_runs,
            "run_success_rate": round((succeeded_runs / max(1, total_runs)) * 100, 2),
            "total_verified_claims": total_claims,
            "reproduced_claims": reproduced_claims,
            "claim_reproducibility_rate": round((reproduced_claims / max(1, total_claims)) * 100, 2),
            "average_reproducibility_score": round(float(avg_score), 4),
        }
