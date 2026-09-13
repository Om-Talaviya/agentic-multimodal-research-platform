"""Repository for managing research automation schedules, sweep results, and alerts."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models.automation import (
    DBAutomationAlert,
    DBResearchSweepResult,
    DBScheduledResearch,
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class AutomationRepository:
    """Repository handling CRUD operations for Research Automation and Scheduled Sweeps."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # -------------------------------------------------------------------------
    # Schedule Management
    # -------------------------------------------------------------------------

    async def create_schedule(
        self,
        user_id: uuid.UUID,
        title: str,
        query_topic: str,
        cron_expression: str = "0 9 * * 1-5",
        routing_profile: str = "balanced",
        source_types: Optional[List[str]] = None,
        novelty_threshold: float = 0.30,
        confidence_threshold: float = 0.85,
        contradiction_alert: bool = True,
        webhook_url: Optional[str] = None,
        email_notifications: Optional[List[str]] = None,
        workspace_id: Optional[uuid.UUID] = None,
        next_run_at: Optional[datetime] = None,
    ) -> DBScheduledResearch:
        schedule = DBScheduledResearch(
            id=uuid.uuid4(),
            user_id=user_id,
            workspace_id=workspace_id,
            title=title.strip(),
            query_topic=query_topic.strip(),
            cron_expression=cron_expression.strip(),
            routing_profile=routing_profile,
            source_types=source_types if source_types is not None else ["web", "academic", "knowledge_vault"],
            novelty_threshold=novelty_threshold,
            confidence_threshold=confidence_threshold,
            contradiction_alert=contradiction_alert,
            webhook_url=webhook_url.strip() if webhook_url else None,
            email_notifications=email_notifications or [],
            status="active",
            total_sweeps_count=0,
            next_run_at=next_run_at or utc_now(),
            created_at=utc_now(),
            updated_at=utc_now(),
        )
        self.session.add(schedule)
        await self.session.commit()
        await self.session.refresh(schedule)
        return schedule

    async def get_schedule(self, schedule_id: uuid.UUID) -> Optional[DBScheduledResearch]:
        stmt = select(DBScheduledResearch).where(DBScheduledResearch.id == schedule_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_schedules(
        self,
        user_id: Optional[uuid.UUID] = None,
        workspace_id: Optional[uuid.UUID] = None,
        status: Optional[str] = None,
        limit: int = 50,
    ) -> List[DBScheduledResearch]:
        stmt = select(DBScheduledResearch)
        if user_id:
            stmt = stmt.where(DBScheduledResearch.user_id == user_id)
        if workspace_id:
            stmt = stmt.where(DBScheduledResearch.workspace_id == workspace_id)
        if status:
            stmt = stmt.where(DBScheduledResearch.status == status)

        stmt = stmt.order_by(desc(DBScheduledResearch.created_at)).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_schedule(
        self,
        schedule_id: uuid.UUID,
        **kwargs: Any,
    ) -> Optional[DBScheduledResearch]:
        schedule = await self.get_schedule(schedule_id)
        if not schedule:
            return None

        for key, value in kwargs.items():
            if hasattr(schedule, key):
                setattr(schedule, key, value)

        schedule.updated_at = utc_now()
        await self.session.commit()
        await self.session.refresh(schedule)
        return schedule

    async def pause_schedule(self, schedule_id: uuid.UUID) -> Optional[DBScheduledResearch]:
        return await self.update_schedule(schedule_id, status="paused")

    async def resume_schedule(self, schedule_id: uuid.UUID) -> Optional[DBScheduledResearch]:
        return await self.update_schedule(schedule_id, status="active")

    async def delete_schedule(self, schedule_id: uuid.UUID) -> bool:
        schedule = await self.get_schedule(schedule_id)
        if not schedule:
            return False
        await self.session.delete(schedule)
        await self.session.commit()
        return True

    # -------------------------------------------------------------------------
    # Sweep Result Management
    # -------------------------------------------------------------------------

    async def record_sweep_result(
        self,
        schedule_id: uuid.UUID,
        job_id: Optional[uuid.UUID] = None,
        status: str = "completed",
        findings_count: int = 0,
        novel_claims_count: int = 0,
        novelty_score: float = 0.0,
        novel_claims: Optional[List[Dict[str, Any]]] = None,
        contradictions_found: Optional[List[Dict[str, Any]]] = None,
        alert_dispatched: bool = False,
        execution_duration_ms: float = 0.0,
        findings_summary: Optional[str] = None,
    ) -> DBResearchSweepResult:
        sweep = DBResearchSweepResult(
            id=uuid.uuid4(),
            schedule_id=schedule_id,
            job_id=job_id,
            status=status,
            findings_count=findings_count,
            novel_claims_count=novel_claims_count,
            novelty_score=novelty_score,
            novel_claims=novel_claims or [],
            contradictions_found=contradictions_found or [],
            alert_dispatched=alert_dispatched,
            execution_duration_ms=execution_duration_ms,
            executed_at=utc_now(),
        )
        self.session.add(sweep)

        # Update schedule stats
        schedule = await self.get_schedule(schedule_id)
        if schedule:
            schedule.total_sweeps_count += 1
            schedule.last_run_at = utc_now()
            if findings_summary:
                schedule.last_findings_summary = findings_summary
            schedule.updated_at = utc_now()

        await self.session.commit()
        await self.session.refresh(sweep)
        return sweep

    async def list_sweep_results(
        self,
        schedule_id: Optional[uuid.UUID] = None,
        limit: int = 50,
    ) -> List[DBResearchSweepResult]:
        stmt = select(DBResearchSweepResult)
        if schedule_id:
            stmt = stmt.where(DBResearchSweepResult.schedule_id == schedule_id)
        stmt = stmt.order_by(desc(DBResearchSweepResult.executed_at)).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # -------------------------------------------------------------------------
    # Alert Management
    # -------------------------------------------------------------------------

    async def create_alert(
        self,
        schedule_id: uuid.UUID,
        title: str,
        message: str,
        severity: str = "info",
        channel: str = "in_app",
        payload: Optional[Dict[str, Any]] = None,
        sweep_id: Optional[uuid.UUID] = None,
        job_id: Optional[uuid.UUID] = None,
        workspace_id: Optional[uuid.UUID] = None,
    ) -> DBAutomationAlert:
        alert = DBAutomationAlert(
            id=uuid.uuid4(),
            schedule_id=schedule_id,
            sweep_id=sweep_id,
            job_id=job_id,
            workspace_id=workspace_id,
            title=title.strip(),
            severity=severity,
            channel=channel,
            message=message.strip(),
            payload=payload or {},
            is_acknowledged=False,
            created_at=utc_now(),
        )
        self.session.add(alert)
        await self.session.commit()
        await self.session.refresh(alert)
        return alert

    async def list_alerts(
        self,
        workspace_id: Optional[uuid.UUID] = None,
        schedule_id: Optional[uuid.UUID] = None,
        is_acknowledged: Optional[bool] = None,
        limit: int = 50,
    ) -> List[DBAutomationAlert]:
        stmt = select(DBAutomationAlert)
        if workspace_id:
            stmt = stmt.where(DBAutomationAlert.workspace_id == workspace_id)
        if schedule_id:
            stmt = stmt.where(DBAutomationAlert.schedule_id == schedule_id)
        if is_acknowledged is not None:
            stmt = stmt.where(DBAutomationAlert.is_acknowledged == is_acknowledged)

        stmt = stmt.order_by(desc(DBAutomationAlert.created_at)).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def acknowledge_alert(self, alert_id: uuid.UUID) -> Optional[DBAutomationAlert]:
        stmt = select(DBAutomationAlert).where(DBAutomationAlert.id == alert_id)
        result = await self.session.execute(stmt)
        alert = result.scalar_one_or_none()
        if not alert:
            return None

        alert.is_acknowledged = True
        alert.acknowledged_at = utc_now()
        await self.session.commit()
        await self.session.refresh(alert)
        return alert

    # -------------------------------------------------------------------------
    # Metrics Aggregation
    # -------------------------------------------------------------------------

    async def get_automation_metrics(
        self, workspace_id: Optional[uuid.UUID] = None
    ) -> Dict[str, Any]:
        # Count total and active schedules
        sched_stmt = select(
            func.count(DBScheduledResearch.id).label("total"),
            func.count(DBScheduledResearch.id).filter(DBScheduledResearch.status == "active").label("active"),
        )
        if workspace_id:
            sched_stmt = sched_stmt.where(DBScheduledResearch.workspace_id == workspace_id)

        sched_res = await self.session.execute(sched_stmt)
        sched_row = sched_res.one()
        total_schedules = sched_row.total or 0
        active_schedules = sched_row.active or 0

        # Count sweeps and average novelty
        sweep_stmt = select(
            func.count(DBResearchSweepResult.id).label("total_sweeps"),
            func.avg(DBResearchSweepResult.novelty_score).label("avg_novelty"),
        )
        sweep_res = await self.session.execute(sweep_stmt)
        sweep_row = sweep_res.one()
        total_sweeps = sweep_row.total_sweeps or 0
        avg_novelty = float(sweep_row.avg_novelty or 0.0)

        # Count alerts and unacknowledged alerts
        alert_stmt = select(
            func.count(DBAutomationAlert.id).label("total_alerts"),
            func.count(DBAutomationAlert.id).filter(DBAutomationAlert.is_acknowledged == False).label("unacked_alerts"),
        )
        if workspace_id:
            alert_stmt = alert_stmt.where(DBAutomationAlert.workspace_id == workspace_id)

        alert_res = await self.session.execute(alert_stmt)
        alert_row = alert_res.one()
        total_alerts = alert_row.total_alerts or 0
        unacked_alerts = alert_row.unacked_alerts or 0

        return {
            "total_schedules": total_schedules,
            "active_schedules": active_schedules,
            "total_sweeps": total_sweeps,
            "average_novelty_score": round(avg_novelty, 4),
            "total_alerts": total_alerts,
            "unacknowledged_alerts": unacked_alerts,
        }
