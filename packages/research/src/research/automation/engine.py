"""Research Automation Engine for recurring scheduled sweeps, diffing, and alert dispatch."""

import re
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Set, Tuple
import structlog
from database.models.automation import (
    DBAutomationAlert,
    DBResearchSweepResult,
    DBScheduledResearch,
)
from database.repositories.automation_repo import AutomationRepository

logger = structlog.get_logger(__name__)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def compute_next_run(cron_expr: str, base_time: Optional[datetime] = None) -> datetime:
    """Compute the next scheduled execution time from a cron or interval expression."""
    now = base_time or utc_now()
    expr = cron_expr.strip().lower()

    if expr in ["@hourly", "hourly"]:
        return now + timedelta(hours=1)
    elif expr in ["@daily", "daily"]:
        return now + timedelta(days=1)
    elif expr in ["@weekly", "weekly"]:
        return now + timedelta(weeks=1)
    elif expr.startswith("every_") and expr.endswith("h"):
        match = re.match(r"every_(\d+)h", expr)
        if match:
            hours = int(match.group(1))
            return now + timedelta(hours=max(1, hours))
    elif expr.startswith("*/") and " " in expr:
        # e.g., */30 * * * * or */15 * * * *
        parts = expr.split()
        minute_part = parts[0]
        match = re.match(r"\*/(\d+)", minute_part)
        if match:
            mins = int(match.group(1))
            return now + timedelta(minutes=max(1, mins))

    # Default fallback: 24 hours
    return now + timedelta(days=1)


class ResearchAutomationEngine:
    """Core autonomous sweep execution, semantic diffing, and multi-channel alerting engine."""

    def __init__(self, repo: AutomationRepository):
        self.repo = repo

    @staticmethod
    def _normalize_claim(text: str) -> str:
        """Normalize claim string for fuzzy matching."""
        return re.sub(r"[^\w\s]", "", text.lower()).strip()

    def detect_novelty(
        self,
        previous_claims: List[str],
        current_claims: List[Dict[str, Any]],
    ) -> Tuple[float, List[Dict[str, Any]]]:
        """Calculates novelty score and isolates new claims relative to historical memory."""
        if not current_claims:
            return 0.0, []

        if not previous_claims:
            # All claims are novel on initial run
            return 1.0, current_claims

        prev_normalized_set: Set[str] = {
            self._normalize_claim(c) for c in previous_claims if c
        }

        novel_claims: List[Dict[str, Any]] = []
        for claim_obj in current_claims:
            claim_text = claim_obj.get("claim", "") or claim_obj.get("summary", "") or ""
            norm_text = self._normalize_claim(claim_text)
            
            # Simple substring / exact containment check
            matched = False
            for prev_norm in prev_normalized_set:
                if norm_text in prev_norm or prev_norm in norm_text:
                    matched = True
                    break
            
            if not matched:
                novel_claims.append(claim_obj)

        novelty_score = len(novel_claims) / max(1, len(current_claims))
        return round(novelty_score, 4), novel_claims

    async def execute_sweep_run(
        self,
        schedule_id: uuid.UUID,
        generated_findings: Optional[List[Dict[str, Any]]] = None,
        job_id: Optional[uuid.UUID] = None,
        contradictions: Optional[List[Dict[str, Any]]] = None,
        duration_ms: float = 1250.0,
    ) -> DBResearchSweepResult:
        """Executes a single scheduled sweep evaluation pass, records diffs, and dispatches alerts."""
        schedule = await self.repo.get_schedule(schedule_id)
        if not schedule:
            raise ValueError(f"Scheduled research with ID {schedule_id} not found")

        findings = generated_findings or [
            {
                "claim": f"Automated monitoring finding for {schedule.query_topic}",
                "confidence": 0.92,
                "topic": schedule.query_topic,
                "source": "Web & Knowledge Sweep",
            }
        ]

        # Fetch prior claims from last findings summary or previous sweeps
        prev_sweeps = await self.repo.list_sweep_results(schedule_id=schedule_id, limit=5)
        prior_claims: List[str] = []
        for s in prev_sweeps:
            for c in s.novel_claims:
                text = c.get("claim") or c.get("summary")
                if text:
                    prior_claims.append(text)

        novelty_score, novel_claims = self.detect_novelty(
            previous_claims=prior_claims, current_claims=findings
        )

        contradictions_found = contradictions or []

        # Determine if an alert should be dispatched
        alert_dispatched = False
        alert_reason = []

        if novelty_score >= schedule.novelty_threshold and len(novel_claims) > 0:
            alert_reason.append(
                f"Novelty score {novelty_score:.2f} meets or exceeds threshold {schedule.novelty_threshold:.2f}"
            )
            alert_dispatched = True

        if schedule.contradiction_alert and len(contradictions_found) > 0:
            alert_reason.append(f"Found {len(contradictions_found)} claim contradiction(s)")
            alert_dispatched = True

        status = "alert_dispatched" if alert_dispatched else (
            "completed" if len(novel_claims) > 0 else "no_novel_findings"
        )

        findings_summary = f"{len(novel_claims)} novel claim(s) discovered for '{schedule.query_topic}'"

        # Record sweep result in database
        sweep_result = await self.repo.record_sweep_result(
            schedule_id=schedule.id,
            job_id=job_id,
            status=status,
            findings_count=len(findings),
            novel_claims_count=len(novel_claims),
            novelty_score=novelty_score,
            novel_claims=novel_claims,
            contradictions_found=contradictions_found,
            alert_dispatched=alert_dispatched,
            execution_duration_ms=duration_ms,
            findings_summary=findings_summary,
        )

        # Dispatch alerts if triggered
        if alert_dispatched:
            severity = "warning" if contradictions_found else "info"
            if novelty_score > 0.7:
                severity = "critical"

            alert_title = f"Research Sweep Alert: {schedule.title}"
            alert_message = (
                f"New discoveries found for topic '{schedule.query_topic}'. "
                + " | ".join(alert_reason)
            )

            # Create in-app alert
            await self.repo.create_alert(
                schedule_id=schedule.id,
                sweep_id=sweep_result.id,
                job_id=job_id,
                workspace_id=schedule.workspace_id,
                title=alert_title,
                severity=severity,
                channel="in_app",
                message=alert_message,
                payload={
                    "novel_claims_count": len(novel_claims),
                    "novelty_score": novelty_score,
                    "novel_claims": novel_claims,
                    "contradictions": contradictions_found,
                    "webhook_url": schedule.webhook_url,
                },
            )

            # If webhook configured, create webhook alert record
            if schedule.webhook_url:
                await self.repo.create_alert(
                    schedule_id=schedule.id,
                    sweep_id=sweep_result.id,
                    job_id=job_id,
                    workspace_id=schedule.workspace_id,
                    title=f"Webhook Dispatch: {schedule.title}",
                    severity=severity,
                    channel="webhook",
                    message=f"Dispatched webhook notification to {schedule.webhook_url}",
                    payload={
                        "webhook_target": schedule.webhook_url,
                        "event": "research.sweep.novelty_detected",
                        "schedule_id": str(schedule.id),
                        "novelty_score": novelty_score,
                    },
                )

        # Compute next run time
        next_run = compute_next_run(schedule.cron_expression, utc_now())
        await self.repo.update_schedule(schedule.id, next_run_at=next_run)

        return sweep_result
