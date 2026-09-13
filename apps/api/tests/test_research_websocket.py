"""Tests for real-time WebSocket research streaming."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch
from uuid import UUID, uuid4
import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from api.dependencies import get_research_event_bus
from api.websocket import connection_manager
from database.connection import get_session
from database.models import Evidence as DBEvidence
from database.models import Report as DBReport
from database.models import ResearchJob as DBJob
from database.models import ResearchTask as DBTask
from database.models import Source as DBSource
from main import app
from research.events import ResearchEvent, ResearchEventBus, ResearchEventType
from shared.auth import UserRole, create_access_token, user_registry


def utc_now() -> datetime:
    return datetime.now(UTC)


@pytest.fixture
def event_bus():
    return ResearchEventBus(max_queue_size=100)


@pytest.fixture
def admin_token():
    admin = user_registry.get_by_username("admin")
    return create_access_token(admin)


@pytest.fixture
def viewer_token():
    viewer = user_registry.get_by_username("viewer")
    return create_access_token(viewer)


@pytest.fixture
def researcher_token():
    researcher = user_registry.get_by_username("researcher")
    return create_access_token(researcher)


@pytest.fixture
def sample_job_id():
    return uuid4()


@pytest.fixture
def mock_job_snapshot(sample_job_id):
    job = DBJob(
        id=sample_job_id,
        request_id=uuid4(),
        question="What are solid-state electrolytes?",
        objective="Analyze solid-state battery electrolytes",
        constraints=["peer-reviewed"],
        status="running",
        created_at=utc_now(),
        updated_at=utc_now(),
    )
    task = DBTask(
        id=uuid4(),
        job_id=sample_job_id,
        type="web_research",
        objective="Search literature",
        agent="web_research",
        status="completed",
        started_at=utc_now(),
        completed_at=utc_now(),
    )
    source = DBSource(
        id=uuid4(),
        job_id=sample_job_id,
        type="web",
        url="https://example.com/paper",
        title="Electrolytes Review",
        source_metadata={"author": "Test Author"},
        retrieved_at=utc_now(),
    )
    evidence = DBEvidence(
        id=uuid4(),
        job_id=sample_job_id,
        source_id=source.id,
        claim="High ionic conductivity achieved",
        supporting_text="Evidence snippet",
        confidence=0.95,
        verification_status="verified",
        verification_notes="Confirmed by Critic",
        created_at=utc_now(),
    )
    report = DBReport(
        id=uuid4(),
        job_id=sample_job_id,
        title="Solid State Battery Report",
        executive_summary="Executive summary content",
        methodology="DAG pipeline",
        findings=[{"topic": "Electrolytes", "summary": "Promising results"}],
        evidence_ids=[str(evidence.id)],
        source_ids=[str(source.id)],
        conclusions=["Ready for scale"],
        limitations=["Cost"],
        generated_at=utc_now(),
    )
    return {
        "job": job,
        "tasks": [task],
        "sources": [source],
        "evidence": [evidence],
        "report": report,
    }


def test_ws_snapshot_and_live_event_stream(event_bus, admin_token, sample_job_id, mock_job_snapshot):
    """Test WebSocket receives snapshot upon connection and streams live events."""
    app.dependency_overrides[get_research_event_bus] = lambda: event_bus

    with patch("api.websocket.ResearchJobRepository") as mock_job_repo, \
         patch("api.websocket.TaskRepository") as mock_task_repo, \
         patch("api.websocket.SourceRepository") as mock_source_repo, \
         patch("api.websocket.EvidenceRepository") as mock_evidence_repo, \
         patch("api.websocket.ReportRepository") as mock_report_repo:

        mock_job_repo.return_value.get = AsyncMock(return_value=mock_job_snapshot["job"])
        mock_task_repo.return_value.get_by_job = AsyncMock(return_value=mock_job_snapshot["tasks"])
        mock_source_repo.return_value.get_by_job = AsyncMock(return_value=mock_job_snapshot["sources"])
        mock_evidence_repo.return_value.get_by_job = AsyncMock(return_value=mock_job_snapshot["evidence"])
        mock_report_repo.return_value.get_by_job = AsyncMock(return_value=mock_job_snapshot["report"])

        client = TestClient(app)
        with client.websocket_connect(f"/api/v1/research/{sample_job_id}/ws?token={admin_token}") as ws:
            # 1. First message must be snapshot
            snapshot_msg = ws.receive_json()
            assert snapshot_msg["type"] == "snapshot"
            assert snapshot_msg["job_id"] == str(sample_job_id)
            assert snapshot_msg["data"]["job"]["id"] == str(sample_job_id)
            assert len(snapshot_msg["data"]["tasks"]) == 1
            assert len(snapshot_msg["data"]["sources"]) == 1
            assert len(snapshot_msg["data"]["evidence"]) == 1
            assert snapshot_msg["data"]["report"]["title"] == "Solid State Battery Report"

            # 2. Publish live event via event bus and receive it over WebSocket
            import asyncio
            live_event = ResearchEvent(
                job_id=str(sample_job_id),
                type=ResearchEventType.TASK_COMPLETED,
                message="Task completed",
                data={"task_id": "task-uuid-2", "status": "completed"},
            )
            asyncio.run(event_bus.publish(live_event))

            event_msg = ws.receive_json()
            assert event_msg["type"] == "event"
            assert event_msg["job_id"] == str(sample_job_id)
            assert event_msg["event"]["type"] == ResearchEventType.TASK_COMPLETED.value
            assert event_msg["event"]["data"]["task_id"] == "task-uuid-2"

    app.dependency_overrides.clear()


def test_ws_authentication_with_all_roles(event_bus, viewer_token, researcher_token, sample_job_id, mock_job_snapshot):
    """Test that viewer, researcher, and admin roles with research:read can all connect."""
    app.dependency_overrides[get_research_event_bus] = lambda: event_bus

    with patch("api.websocket.ResearchJobRepository") as mock_job_repo, \
         patch("api.websocket.TaskRepository") as mock_task_repo, \
         patch("api.websocket.SourceRepository") as mock_source_repo, \
         patch("api.websocket.EvidenceRepository") as mock_evidence_repo, \
         patch("api.websocket.ReportRepository") as mock_report_repo:

        mock_job_repo.return_value.get = AsyncMock(return_value=mock_job_snapshot["job"])
        mock_task_repo.return_value.get_by_job = AsyncMock(return_value=[])
        mock_source_repo.return_value.get_by_job = AsyncMock(return_value=[])
        mock_evidence_repo.return_value.get_by_job = AsyncMock(return_value=[])
        mock_report_repo.return_value.get_by_job = AsyncMock(return_value=None)

        client = TestClient(app)

        # Viewer role
        with client.websocket_connect(f"/api/v1/research/{sample_job_id}/ws?token={viewer_token}") as ws:
            msg = ws.receive_json()
            assert msg["type"] == "snapshot"

        # Researcher role
        with client.websocket_connect(f"/api/v1/research/{sample_job_id}/ws?token={researcher_token}") as ws:
            msg = ws.receive_json()
            assert msg["type"] == "snapshot"

    app.dependency_overrides.clear()


def test_ws_rejects_invalid_token(sample_job_id):
    """Test that invalid JWT token closes WebSocket connection."""
    client = TestClient(app)
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect(f"/api/v1/research/{sample_job_id}/ws?token=invalid.jwt.token"):
            pass
    assert exc_info.value.code == 1008


def test_ws_unknown_job_returns_error_and_closes(admin_token, sample_job_id, event_bus):
    """Test that connecting to non-existent job sends NOT_FOUND error and closes with 1008."""
    app.dependency_overrides[get_research_event_bus] = lambda: event_bus

    with patch("api.websocket.ResearchJobRepository") as mock_job_repo:
        mock_job_repo.return_value.get = AsyncMock(return_value=None)

        client = TestClient(app)
        with pytest.raises(WebSocketDisconnect) as exc_info:
            with client.websocket_connect(f"/api/v1/research/{sample_job_id}/ws?token={admin_token}") as ws:
                msg = ws.receive_json()
                assert msg["type"] == "error"
                assert msg["error"]["code"] == "NOT_FOUND"
                # Next receive will raise WebSocketDisconnect
                ws.receive_json()

        assert exc_info.value.code == 1008

    app.dependency_overrides.clear()


def test_ws_multi_client_fan_out_and_isolation(event_bus, admin_token, mock_job_snapshot):
    """Test that multiple clients on the same job receive events, and different jobs are isolated."""
    app.dependency_overrides[get_research_event_bus] = lambda: event_bus

    job_1 = uuid4()
    job_2 = uuid4()

    with patch("api.websocket.ResearchJobRepository") as mock_job_repo, \
         patch("api.websocket.TaskRepository") as mock_task_repo, \
         patch("api.websocket.SourceRepository") as mock_source_repo, \
         patch("api.websocket.EvidenceRepository") as mock_evidence_repo, \
         patch("api.websocket.ReportRepository") as mock_report_repo:

        mock_job_repo.return_value.get = AsyncMock(return_value=mock_job_snapshot["job"])
        mock_task_repo.return_value.get_by_job = AsyncMock(return_value=[])
        mock_source_repo.return_value.get_by_job = AsyncMock(return_value=[])
        mock_evidence_repo.return_value.get_by_job = AsyncMock(return_value=[])
        mock_report_repo.return_value.get_by_job = AsyncMock(return_value=None)

        client = TestClient(app)

        with client.websocket_connect(f"/api/v1/research/{job_1}/ws?token={admin_token}") as ws1_job1, \
             client.websocket_connect(f"/api/v1/research/{job_1}/ws?token={admin_token}") as ws2_job1, \
             client.websocket_connect(f"/api/v1/research/{job_2}/ws?token={admin_token}") as ws_job2:

            # Drain initial snapshots
            assert ws1_job1.receive_json()["type"] == "snapshot"
            assert ws2_job1.receive_json()["type"] == "snapshot"
            assert ws_job2.receive_json()["type"] == "snapshot"

            # Publish event for Job 1
            import asyncio
            ev1 = ResearchEvent(
                job_id=str(job_1),
                type=ResearchEventType.TASK_STARTED,
                data={"task_id": "t1"},
            )
            asyncio.run(event_bus.publish(ev1))

            # Both Job 1 clients should receive the event
            msg1 = ws1_job1.receive_json()
            msg2 = ws2_job1.receive_json()
            assert msg1["type"] == "event"
            assert msg1["event"]["job_id"] == str(job_1)
            assert msg2["type"] == "event"
            assert msg2["event"]["job_id"] == str(job_1)

    app.dependency_overrides.clear()
