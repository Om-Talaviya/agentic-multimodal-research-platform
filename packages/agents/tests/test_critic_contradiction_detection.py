"""Unit tests for CriticAgent contradiction detection and confidence scoring."""

import json
from unittest.mock import AsyncMock, MagicMock
import pytest
from agents.base import AgentContext
from agents.critic.critic_agent import CriticAgent
from agents.memory import AgentMemory
from research.models import ResearchTask
from ai.schemas import LLMResponse


@pytest.mark.asyncio
async def test_critic_agent_detects_contradictions():
    """CriticAgent parses and classifies contradictions between conflicting claims."""
    mock_llm = MagicMock()
    mock_llm.complete = AsyncMock(
        return_value=LLMResponse(
            content=json.dumps({
                "verifications": [
                    {
                        "evidence_id": "ev_1",
                        "claim": "Dataset size is 50,000 samples.",
                        "verification_status": "verified",
                        "confidence": 0.95,
                        "source_reliability": 1.0,
                        "verification_notes": "Directly stated in Section 2."
                    },
                    {
                        "evidence_id": "ev_2",
                        "claim": "Dataset size is 35,000 samples.",
                        "verification_status": "inconclusive",
                        "confidence": 0.60,
                        "source_reliability": 0.8,
                        "verification_notes": "Preliminary estimate before data cleaning."
                    }
                ],
                "contradictions": [
                    {
                        "topic": "Dataset Sample Count",
                        "claim_a": "Dataset size is 50,000 samples.",
                        "source_a": "Paper 1 (Section 2)",
                        "claim_b": "Dataset size is 35,000 samples.",
                        "source_b": "Blog Post Preliminary",
                        "conflict_type": "numerical_discrepancy",
                        "explanation": "Paper 1 counts augmented samples whereas Blog post counts raw samples.",
                        "severity": "medium"
                    }
                ],
                "confidence_score": 0.82,
                "quality_score": 0.88,
                "critique_summary": "High factual grounding with one resolved numerical discrepancy."
            }),
            model="gemini-2.5-pro",
            usage={"prompt_tokens": 350, "completion_tokens": 150, "total_tokens": 500},
        )
    )

    mock_router = MagicMock()
    mock_router.select_llm.return_value = mock_llm

    agent = CriticAgent()
    task = ResearchTask(
        id="task_critic_contra_1",
        job_id="job_contra_1",
        type="critic",
        objective="Verify dataset scale claims",
        agent="critic",
        inputs={
            "evidence": [
                {
                    "id": "ev_1",
                    "claim": "Dataset size is 50,000 samples.",
                    "supporting_text": "We curated a total of 50,000 samples.",
                    "source_id": "src_1",
                    "source_reliability": 1.0,
                    "citation_coordinates": {"page_number": 2, "paragraph_index": 3}
                },
                {
                    "id": "ev_2",
                    "claim": "Dataset size is 35,000 samples.",
                    "supporting_text": "Our dataset contains around 35,000 items.",
                    "source_id": "src_2",
                    "source_reliability": 0.8,
                    "citation_coordinates": {"page_number": 1}
                }
            ],
            "question": "What is the true dataset size?"
        }
    )

    context = AgentContext(
        research_job_id="job_contra_1",
        task_id="task_critic_contra_1",
        request_id="req_contra_1",
        tools={},
        memory=AgentMemory(),
        model_router=mock_router,
        config={},
    )

    result = await agent.run(task, context)

    assert result.success is True
    assert result.output["confidence_score"] == 0.82
    assert len(result.output["contradictions"]) == 1
    contradiction = result.output["contradictions"][0]
    assert contradiction["conflict_type"] == "numerical_discrepancy"
    assert contradiction["topic"] == "Dataset Sample Count"
    assert context.memory.get_working("last_confidence_score") == 0.82
    assert len(context.memory.get_working("last_contradictions")) == 1
