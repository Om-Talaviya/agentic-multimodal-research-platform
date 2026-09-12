"""Unit tests for CriticAgent deep gap analysis, hypothesis extraction, and multi-round reflection (Phase 15)."""

from unittest.mock import AsyncMock, MagicMock
import pytest

from agents.critic.critic_agent import CriticAgent
from research.models import ResearchTask
from ai.schemas import LLMResponse


@pytest.mark.asyncio
async def test_critic_agent_deep_gaps_and_hypotheses():
    """CriticAgent parses unresolved_gaps, gap_queries, and suggested_hypotheses from model output."""
    mock_llm_json = """{
        "verifications": [
            {
                "evidence_id": "ev_101",
                "claim": "Model A latency is 12ms",
                "verification_status": "inconclusive",
                "confidence": 0.65,
                "verification_notes": "Benchmark batch size was omitted."
            }
        ],
        "contradictions": [
            {
                "topic": "Inference Latency",
                "claim_a": "Latency is 12ms",
                "source_a": "Source 1",
                "claim_b": "Latency is 45ms",
                "source_b": "Source 2",
                "conflict_type": "methodological_divergence",
                "explanation": "Different hardware (A100 vs H100) and batch sizes.",
                "severity": "medium"
            }
        ],
        "unresolved_gaps": [
            "Missing hardware specification and batch size for Source 1"
        ],
        "gap_queries": [
            "Model A latency A100 batch size 1 vs H100 batch size 8"
        ],
        "suggested_hypotheses": [
            "Source 1 measured single-token latency on H100 while Source 2 measured TTFT on A100."
        ],
        "confidence_score": 0.68,
        "quality_score": 0.70,
        "critique_summary": "Discrepancy caused by undisclosed hardware differences."
    }"""

    agent = CriticAgent()
    task = ResearchTask(
        id="task_deep_critic_1",
        job_id="job_deep_1",
        type="critic",
        objective="Evaluate latency benchmark claims",
        agent="critic",
        inputs={
            "evidence": [
                {
                    "id": "ev_101",
                    "claim": "Model A latency is 12ms",
                    "supporting_text": "We report 12ms latency.",
                }
            ],
            "question": "What is the inference latency of Model A?",
        },
    )

    context = MagicMock()
    context.research_job_id = "job_deep_1"
    context.memory = MagicMock()
    context.complete_llm = AsyncMock(
        return_value=LLMResponse(
            content=mock_llm_json,
            model="gemini-2.0-flash",
            usage={"prompt_tokens": 100, "completion_tokens": 80},
        )
    )

    result = await agent.run(task, context)

    assert result.success is True
    assert result.output["confidence_score"] == 0.68
    assert len(result.output["unresolved_gaps"]) == 1
    assert "batch size" in result.output["unresolved_gaps"][0]
    assert len(result.output["gap_queries"]) == 1
    assert len(result.output["suggested_hypotheses"]) == 1
    assert len(result.output["contradictions"]) == 1


@pytest.mark.asyncio
async def test_critic_agent_fallback_gap_queries_generation():
    """CriticAgent auto-generates gap_queries from contradictions if model returns empty gap_queries."""
    mock_llm_json = """{
        "verifications": [],
        "contradictions": [
            {
                "topic": "Context Window Scaling",
                "claim_a": "Supports 128k",
                "source_a": "Doc A",
                "claim_b": "Supports 32k",
                "source_b": "Doc B",
                "conflict_type": "direct_conflict",
                "explanation": "Conflicting limits stated.",
                "severity": "high"
            }
        ],
        "unresolved_gaps": [],
        "gap_queries": [],
        "suggested_hypotheses": [],
        "confidence_score": 0.55,
        "quality_score": 0.60,
        "critique_summary": "Direct conflict on context limit."
    }"""

    agent = CriticAgent()
    task = ResearchTask(
        id="task_deep_critic_2",
        job_id="job_deep_2",
        type="critic",
        objective="Verify context limits",
        agent="critic",
        inputs={
            "evidence": [
                {"id": "ev_1", "claim": "Supports 128k", "supporting_text": "128k context"},
            ],
            "question": "What is the context window?",
        },
    )

    context = MagicMock()
    context.memory = MagicMock()
    context.complete_llm = AsyncMock(
        return_value=LLMResponse(
            content=mock_llm_json,
            model="gemini-2.0-flash",
            usage={},
        )
    )

    result = await agent.run(task, context)

    assert result.success is True
    # Should automatically generate fallback query for the contradiction topic
    assert len(result.output["gap_queries"]) == 1
    assert "Context Window Scaling" in result.output["gap_queries"][0]
