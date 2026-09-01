"""WebSocket endpoints and connection management."""

from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status

from api.dependencies import get_research_event_bus
from database.connection import get_session
from database.repositories import (
    EvidenceRepository,
    ReportRepository,
    ResearchJobRepository,
    SourceRepository,
    TaskRepository,
    UserRepository,
)
from research.events import ResearchEventBus
from shared.auth import User, user_registry, verify_token
from shared.config import settings
from shared.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/research", tags=["research"])


class ConnectionManager:
    """Track active WebSocket clients by research job."""

    def __init__(self) -> None:
        self._connections: dict[str, set[WebSocket]] = defaultdict(set)
        self._lock = asyncio.Lock()

    async def connect(self, job_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._connections[job_id].add(websocket)

    def disconnect(self, job_id: str, websocket: WebSocket) -> None:
        connections = self._connections.get(job_id)
        if connections is None:
            return
        connections.discard(websocket)
        if not connections:
            self._connections.pop(job_id, None)

    async def send_json(self, websocket: WebSocket, payload: dict[str, Any]) -> None:
        await websocket.send_json(payload)

    def connection_count(self, job_id: str) -> int:
        return len(self._connections.get(job_id, set()))


connection_manager = ConnectionManager()


def _serialize_job(job: Any) -> dict[str, Any]:
    return {
        "id": str(job.id),
        "request_id": str(job.request_id),
        "question": job.question,
        "objective": job.objective,
        "domain": job.domain,
        "scope": job.scope,
        "constraints": job.constraints or [],
        "expected_output": job.expected_output,
        "status": job.status,
        "created_at": job.created_at.isoformat() if hasattr(job.created_at, "isoformat") else str(job.created_at),
        "updated_at": job.updated_at.isoformat() if hasattr(job.updated_at, "isoformat") else str(job.updated_at),
        "completed_at": job.completed_at.isoformat() if job.completed_at and hasattr(job.completed_at, "isoformat") else str(job.completed_at) if job.completed_at else None,
        "error_message": job.error_message,
    }


def _serialize_task(task: Any) -> dict[str, Any]:
    return {
        "id": str(task.id),
        "job_id": str(task.job_id),
        "type": task.type,
        "objective": task.objective,
        "agent": task.agent,
        "status": task.status,
        "started_at": task.started_at.isoformat() if task.started_at and hasattr(task.started_at, "isoformat") else str(task.started_at) if task.started_at else None,
        "completed_at": task.completed_at.isoformat() if task.completed_at and hasattr(task.completed_at, "isoformat") else str(task.completed_at) if task.completed_at else None,
        "error_message": task.error_message,
        "result": task.result,
    }


def _serialize_source(source: Any) -> dict[str, Any]:
    return {
        "id": str(source.id),
        "type": source.type,
        "url": source.url,
        "title": source.title,
        "metadata": getattr(source, "source_metadata", None) or getattr(source, "metadata", None) or {},
        "retrieved_at": source.retrieved_at.isoformat() if hasattr(source.retrieved_at, "isoformat") else str(source.retrieved_at),
    }


def _serialize_evidence(evidence: Any) -> dict[str, Any]:
    return {
        "id": str(evidence.id),
        "source_id": str(evidence.source_id),
        "claim": evidence.claim,
        "supporting_text": evidence.supporting_text,
        "confidence": evidence.confidence,
        "verification_status": evidence.verification_status,
        "verification_notes": evidence.verification_notes,
    }


def _serialize_report(report: Any) -> dict[str, Any] | None:
    if report is None:
        return None
    return {
        "id": str(report.id),
        "job_id": str(report.job_id),
        "title": report.title,
        "executive_summary": report.executive_summary or "",
        "methodology": report.methodology or "",
        "findings": report.findings or [],
        "evidence": getattr(report, "evidence_ids", None) or getattr(report, "evidence", None) or [],
        "sources": getattr(report, "source_ids", None) or getattr(report, "sources", None) or [],
        "conclusions": report.conclusions or [],
        "limitations": report.limitations or [],
        "generated_at": report.generated_at.isoformat() if hasattr(report.generated_at, "isoformat") else str(report.generated_at),
    }


async def _authenticate_websocket(websocket: WebSocket, session: Any) -> User | None:
    token = websocket.query_params.get("token")
    if not token:
        auth_header = websocket.headers.get("authorization")
        if auth_header and auth_header.lower().startswith("bearer "):
            token = auth_header[7:].strip()
        elif "sec-websocket-protocol" in websocket.headers:
            protocols = [p.strip() for p in websocket.headers["sec-websocket-protocol"].split(",")]
            for p in protocols:
                if p and p.lower() != "bearer":
                    token = p
                    break

    repo = UserRepository(session)

    if not token:
        if settings.debug:
            try:
                admin_db = await repo.get_by_username("admin")
                if admin_db and admin_db.is_active:
                    return User.from_db(admin_db)
            except Exception:
                pass
            admin_mem = user_registry.get_by_username("admin")
            if admin_mem:
                return admin_mem
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return None

    try:
        payload = verify_token(token, expected_type="access")
        from uuid import UUID
        db_user = None
        try:
            try:
                db_user = await repo.get_by_id(UUID(payload.sub))
            except (ValueError, TypeError):
                db_user = await repo.get_by_username(payload.username)
        except Exception:
            db_user = None

        if db_user:
            if not db_user.is_active:
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                return None
            user = User.from_db(db_user)
        else:
            mem_user = user_registry.get_by_id(payload.sub) or user_registry.get_by_username(payload.username)
            if not mem_user or not mem_user.is_active:
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                return None
            user = mem_user

        if not user.has_permission("research:read"):
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return None
        return user
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return None



async def _build_snapshot(session: Any, job_id: UUID) -> dict[str, Any] | None:
    job_repo = ResearchJobRepository(session)
    job = await job_repo.get(job_id)
    if not job:
        return None

    task_repo = TaskRepository(session)
    source_repo = SourceRepository(session)
    evidence_repo = EvidenceRepository(session)
    report_repo = ReportRepository(session)

    tasks = await task_repo.get_by_job(job_id)
    sources = await source_repo.get_by_job(job_id)
    evidence = await evidence_repo.get_by_job(job_id)
    report = await report_repo.get_by_job(job_id)

    return {
        "job": _serialize_job(job),
        "tasks": [_serialize_task(task) for task in tasks],
        "sources": [_serialize_source(source) for source in sources],
        "evidence": [_serialize_evidence(item) for item in evidence],
        "report": _serialize_report(report),
    }


@router.websocket("/{job_id}/ws")
async def research_job_websocket(
    websocket: WebSocket,
    job_id: UUID,
    event_bus: ResearchEventBus = Depends(get_research_event_bus),
) -> None:
    async with get_session() as session:
        user = await _authenticate_websocket(websocket, session)
        if user is None:
            return

        job_id_str = str(job_id)
        await connection_manager.connect(job_id_str, websocket)
        logger.info("Research WebSocket connected", job_id=job_id_str, user_id=user.id)

        try:
            # Subscribe before loading the snapshot to prevent race conditions with background execution
            async with event_bus.subscribe(job_id_str) as queue:
                snapshot = await _build_snapshot(session, job_id)

                if snapshot is None:
                    await connection_manager.send_json(
                        websocket,
                        {"type": "error", "error": {"code": "NOT_FOUND", "message": "Research job not found"}},
                    )
                    await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                    return

                await connection_manager.send_json(
                    websocket,
                    {"type": "snapshot", "job_id": job_id_str, "data": snapshot},
                )

                while True:
                    try:
                        event = await asyncio.wait_for(queue.get(), timeout=30)
                        await connection_manager.send_json(
                            websocket,
                            {"type": "event", "job_id": job_id_str, "event": event.to_payload()},
                        )
                    except TimeoutError:
                        await connection_manager.send_json(
                            websocket,
                            {"type": "heartbeat", "job_id": job_id_str},
                        )
        except WebSocketDisconnect:
            pass
        except Exception as exc:
            logger.warning("WebSocket error", job_id=job_id_str, error=str(exc))
        finally:
            connection_manager.disconnect(job_id_str, websocket)
            logger.info("Research WebSocket disconnected", job_id=job_id_str, user_id=user.id)
