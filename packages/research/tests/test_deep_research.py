"""Unit tests for Autonomous Deep Research Engine and recursive hypothesis loops (Phase 15)."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
import pytest

from research.models import (
    Contradiction,
    DeepResearchConfig,
    Evidence,
    ResearchIteration,
    ResearchJob,
    ResearchPlan,
    ResearchStep,
)
from research.events import ResearchEvent, ResearchEventBus, ResearchEventType
from research.deep_research import DeepResearchEngine


def test_deep_research_config_and_iteration_models():
    """Verify DeepResearchConfig and ResearchIteration data models and field constraints."""
    config = DeepResearchConfig(
        enabled=True,
        max_iterations=4,
        min_confidence_threshold=0.90,
        max_spawned_per_round=5,
        diminishing_returns_threshold=0.03,
    )
    assert config.max_iterations == 4
    assert config.min_confidence_threshold == 0.90
    assert config.max_spawned_per_round == 5
    assert config.diminishing_returns_threshold == 0.03

    iteration = ResearchIteration(
        iteration_index=1,
        hypotheses=["Hypothesis A: Data discrepancy due to batch size differences."],
        unresolved_gaps=["Missing evaluation on benchmark GSM8K."],
        gap_queries=["GSM8K benchmark performance for model X"],
        confidence_score=0.82,
        confidence_delta=0.12,
        spawned_task_count=2,
        is_converged=False,
    )
    assert iteration.iteration_index == 1
    assert len(iteration.hypotheses) == 1
    assert iteration.confidence_delta == 0.12
    assert iteration.is_converged is False


@pytest.mark.asyncio
async def test_deep_research_immediate_convergence():
    """Verify that if initial verification meets the target threshold, DeepResearchEngine converges immediately."""
    pipeline_mock = MagicMock()
    pipeline_mock.orchestrator = MagicMock()
    pipeline_mock.event_bus = MagicMock()
    pipeline_mock.event_bus.publish = AsyncMock()

    engine = DeepResearchEngine(pipeline_mock)

    job = ResearchJob(
        id=str(uuid4()),
        question="What is the architecture of Llama 3?",
        objective="Analyze Llama 3 architecture",
    )
    plan = ResearchPlan(objective=job.objective)

    initial_verif = {
        "verifications": [{"evidence_id": "ev_1", "verification_status": "verified"}],
        "contradictions": [],
        "unresolved_gaps": [],
        "gap_queries": [],
        "suggested_hypotheses": [],
        "confidence_score": 0.92,
    }

    config = DeepResearchConfig(min_confidence_threshold=0.85)

    verif, iterations = await engine.execute_deep_research(job, plan, initial_verif, config=config)

    assert len(iterations) == 1
    assert iterations[0].is_converged is True
    assert iterations[0].convergence_reason == "initial_threshold_met"
    assert iterations[0].confidence_score == 0.92


@pytest.mark.asyncio
async def test_deep_research_multi_round_convergence():
    """Verify multi-round recursive loop where round 1 executes spawned tasks, updates evidence, and converges in round 2."""
    pipeline_mock = MagicMock()
    pipeline_mock.orchestrator = MagicMock()
    pipeline_mock.orchestrator.create_context = MagicMock()
    pipeline_mock.event_bus = MagicMock()
    pipeline_mock.event_bus.publish = AsyncMock()
    pipeline_mock.execute_plan = AsyncMock()

    # Mock run_verification to return lower confidence on round 1, then high on round 2
    round_counter = 0

    async def mock_run_verification(job):
        nonlocal round_counter
        round_counter += 1
        if round_counter == 1:
            return {
                "verifications": [{"evidence_id": "ev_1", "verification_status": "verified"}],
                "contradictions": [],
                "unresolved_gaps": [],
                "gap_queries": [],
                "suggested_hypotheses": [],
                "confidence_score": 0.91,
            }
        return {
            "verifications": [],
            "contradictions": [],
            "confidence_score": 0.95,
        }

    pipeline_mock.run_verification = mock_run_verification

    engine = DeepResearchEngine(pipeline_mock)

    job = ResearchJob(
        id=str(uuid4()),
        question="What are the conflicting scaling law constants?",
        objective="Investigate scaling law constants",
    )
    plan = ResearchPlan(objective=job.objective)

    initial_verif = {
        "verifications": [],
        "contradictions": [
            {
                "topic": "Compute alpha constant",
                "claim_a": "alpha is 0.05",
                "source_a": "Source 1",
                "claim_b": "alpha is 0.08",
                "source_b": "Source 2",
                "conflict_type": "numerical_discrepancy",
                "explanation": "Different dataset filtering used.",
                "severity": "medium",
            }
        ],
        "unresolved_gaps": ["Compute scaling coefficient difference"],
        "gap_queries": ["Chinchilla compute scaling law alpha exponent dataset filtering"],
        "suggested_hypotheses": ["Hypothesis: Filtering pipeline affected token quality."],
        "confidence_score": 0.65,
    }

    # Mock database session and PlannerAgent
    with patch("database.connection.get_session") as mock_session_ctx, \
         patch("database.repositories.EvidenceRepository") as mock_repo_cls, \
         patch("agents.planner.planner_agent.PlannerAgent.replan") as mock_replan:

        mock_session = AsyncMock()
        mock_session_ctx.return_value.__aenter__.return_value = mock_session
        mock_repo = MagicMock()
        mock_repo.get_by_job = AsyncMock(return_value=[])
        mock_repo_cls.return_value = mock_repo

        mock_replan.return_value = MagicMock(
            success=True,
            output={
                "plan_explanation": "Investigate dataset filtering effects",
                "spawned_steps": [
                    ResearchStep(
                        id="step_dyn_1",
                        name="Search dataset filtering for scaling constants",
                        description="Deep dive into dataset filtering",
                        agent="web_research",
                        inputs={"query": "dataset filtering scaling laws"},
                    )
                ],
            },
        )

        config = DeepResearchConfig(max_iterations=3, min_confidence_threshold=0.85)

        verif, iterations = await engine.execute_deep_research(job, plan, initial_verif, config=config)

        assert len(iterations) == 1
        assert iterations[0].iteration_index == 1
        assert iterations[0].is_converged is True
        assert iterations[0].convergence_reason == "confidence_threshold_met"
        assert iterations[0].confidence_score == 0.91
        assert iterations[0].confidence_delta == round(0.91 - 0.65, 4)
        assert iterations[0].spawned_task_count == 1


@pytest.mark.asyncio
async def test_deep_research_max_iterations_guardrail():
    """Verify that deep research halts when max_iterations is reached."""
    pipeline_mock = MagicMock()
    pipeline_mock.orchestrator = MagicMock()
    pipeline_mock.orchestrator.create_context = MagicMock()
    pipeline_mock.event_bus = MagicMock()
    pipeline_mock.event_bus.publish = AsyncMock()
    pipeline_mock.execute_plan = AsyncMock()

    # Always returns low confidence with persistent contradiction
    async def mock_run_verification(job):
        return {
            "verifications": [],
            "contradictions": [{"topic": "Unresolvable anomaly"}],
            "unresolved_gaps": ["Missing raw telemetry"],
            "gap_queries": ["telemetry search"],
            "confidence_score": 0.60,
        }

    pipeline_mock.run_verification = mock_run_verification

    engine = DeepResearchEngine(pipeline_mock)

    job = ResearchJob(
        id=str(uuid4()),
        question="Complex unresolvable dilemma",
        objective="Deep research unresolvable query",
    )
    plan = ResearchPlan(objective=job.objective)

    initial_verif = {
        "contradictions": [{"topic": "Unresolvable anomaly"}],
        "unresolved_gaps": ["Missing raw telemetry"],
        "confidence_score": 0.55,
    }

    with patch("database.connection.get_session") as mock_session_ctx, \
         patch("database.repositories.EvidenceRepository") as mock_repo_cls, \
         patch("agents.planner.planner_agent.PlannerAgent.replan") as mock_replan:

        mock_session = AsyncMock()
        mock_session_ctx.return_value.__aenter__.return_value = mock_session
        mock_repo = MagicMock()
        mock_repo.get_by_job = AsyncMock(return_value=[])
        mock_repo_cls.return_value = mock_repo

        mock_replan.return_value = MagicMock(
            success=True,
            output={
                "plan_explanation": "Attempt deep resolution",
                "spawned_steps": [
                    ResearchStep(
                        id="step_dyn_sub",
                        name="Subtask investigation",
                        description="Investigate",
                        agent="web_research",
                    )
                ],
            },
        )

        config = DeepResearchConfig(max_iterations=2, min_confidence_threshold=0.85)

        verif, iterations = await engine.execute_deep_research(job, plan, initial_verif, config=config)

        assert len(iterations) == 2
        assert iterations[-1].is_converged is True
        assert iterations[-1].convergence_reason == "max_iterations_reached"


@pytest.mark.asyncio
async def test_deep_research_diminishing_returns_guardrail():
    """Verify that deep research halts when confidence delta between rounds is less than diminishing_returns_threshold."""
    pipeline_mock = MagicMock()
    pipeline_mock.orchestrator = MagicMock()
    pipeline_mock.orchestrator.create_context = MagicMock()
    pipeline_mock.event_bus = MagicMock()
    pipeline_mock.event_bus.publish = AsyncMock()
    pipeline_mock.execute_plan = AsyncMock()

    # Round 1 returns 0.75 (from 0.70, delta 0.05), Round 2 returns 0.755 (delta 0.005 < 0.02 threshold)
    round_count = 0
    async def mock_run_verification(job):
        nonlocal round_count
        round_count += 1
        if round_count == 1:
            return {
                "verifications": [],
                "contradictions": [],
                "unresolved_gaps": ["Minor nuance"],
                "gap_queries": ["nuance query"],
                "confidence_score": 0.75,
            }
        return {
            "verifications": [],
            "contradictions": [],
            "unresolved_gaps": ["Minor nuance"],
            "confidence_score": 0.755,
        }

    pipeline_mock.run_verification = mock_run_verification

    engine = DeepResearchEngine(pipeline_mock)

    job = ResearchJob(
        id=str(uuid4()),
        question="Query with plateauing returns",
        objective="Analyze plateauing query",
    )
    plan = ResearchPlan(objective=job.objective)

    initial_verif = {
        "contradictions": [],
        "unresolved_gaps": ["Minor nuance"],
        "confidence_score": 0.70,
    }

    with patch("database.connection.get_session") as mock_session_ctx, \
         patch("database.repositories.EvidenceRepository") as mock_repo_cls, \
         patch("agents.planner.planner_agent.PlannerAgent.replan") as mock_replan:

        mock_session = AsyncMock()
        mock_session_ctx.return_value.__aenter__.return_value = mock_session
        mock_repo = MagicMock()
        mock_repo.get_by_job = AsyncMock(return_value=[])
        mock_repo_cls.return_value = mock_repo

        mock_replan.return_value = MagicMock(
            success=True,
            output={
                "plan_explanation": "Investigate minor nuance",
                "spawned_steps": [
                    ResearchStep(
                        id="step_dyn_plateau",
                        name="Plateau subtask",
                        description="Investigate nuance",
                        agent="web_research",
                    )
                ],
            },
        )

        config = DeepResearchConfig(max_iterations=5, min_confidence_threshold=0.85, diminishing_returns_threshold=0.02)

        verif, iterations = await engine.execute_deep_research(job, plan, initial_verif, config=config)

        assert len(iterations) == 2
        assert iterations[-1].is_converged is True
        assert iterations[-1].convergence_reason == "diminishing_returns"
