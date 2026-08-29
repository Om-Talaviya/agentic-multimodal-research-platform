"""Unit tests for CriticAgent."""

import json
from unittest.mock import AsyncMock, MagicMock
import pytest
from agents.base import AgentContext
from agents.critic.critic_agent import CriticAgent
from agents.memory import AgentMemory
from research.models import ResearchTask, Evidence
from ai.schemas import LLMResponse


@pytest.mark.asyncio
async def test_critic_agent_with_evidence():
    mock_llm = MagicMock()
    mock_llm.complete = AsyncMock(
        return_value=LLMResponse(
            content=json.dumps({
                "verifications": [
                    {
                        "evidence_id": "ev_1",
                        "claim": "The dataset contains 10,000 multimodal pairs.",
                        "verification_status": "verified",
                        "confidence": 0.95,
                        "verification_notes": "Table 1 directly confirms 10k pairs."
                    }
                ],
                "quality_score": 0.92,
                "critique_summary": "Strong factual grounding."
            }),
            model="gemini-2.5-pro",
            usage={"prompt_tokens": 200, "completion_tokens": 80, "total_tokens": 280},
        )
    )

    mock_router = MagicMock()
    mock_router.select_llm.return_value = mock_llm

    agent = CriticAgent()
    task = ResearchTask(
        id="task_critic_1",
        job_id="job_1",
        type="critic",
        objective="Verify findings for multimodal benchmark",
        agent="critic",
        inputs={
            "evidence": [
                {
                    "id": "ev_1",
                    "claim": "The dataset contains 10,000 multimodal pairs.",
                    "supporting_text": "Table 1 shows 10,000 multimodal image-text pairs collected."
                }
            ],
            "question": "What is the dataset size?"
        }
    )

    context = AgentContext(
        research_job_id="job_1",
        task_id="task_critic_1",
        request_id="req_1",
        tools={},
        memory=AgentMemory(),
        model_router=mock_router,
        config={},
    )

    result = await agent.run(task, context)

    assert result.success is True
    assert result.output["quality_score"] == 0.92
    assert len(result.output["verifications"]) == 1
    assert result.output["verifications"][0]["verification_status"] == "verified"
    assert context.memory.get_working("last_critic_score") == 0.92


@pytest.mark.asyncio
async def test_critic_agent_empty_evidence():
    mock_router = MagicMock()
    agent = CriticAgent()
    task = ResearchTask(
        id="task_critic_2",
        job_id="job_2",
        type="critic",
        objective="Verify findings",
        agent="critic",
        inputs={"evidence": []}
    )

    context = AgentContext(
        research_job_id="job_2",
        task_id="task_critic_2",
        request_id="req_2",
        tools={},
        memory=AgentMemory(),
        model_router=mock_router,
        config={},
    )

    result = await agent.run(task, context)
    assert result.success is True
    assert result.output["quality_score"] == 1.0
    assert len(result.output["verifications"]) == 0
