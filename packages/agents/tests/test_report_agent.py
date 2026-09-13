"""Unit tests for ReportAgent."""

import json
from unittest.mock import AsyncMock, MagicMock
import pytest
from agents.base import AgentContext
from agents.research.report_agent import ReportAgent
from agents.memory import AgentMemory
from research.models import ResearchTask, Evidence, Source, Finding
from ai.schemas import LLMResponse


@pytest.mark.asyncio
async def test_report_agent_with_verified_evidence():
    """ReportAgent can synthesize a report from verified evidence."""
    mock_llm = MagicMock()
    mock_llm.complete = AsyncMock(
        return_value=LLMResponse(
            content=json.dumps({
                "title": "Research Report: AI Safety",
                "executive_summary": "AI safety research shows promising alignment techniques.",
                "methodology": "Literature review of 10 papers on AI alignment.",
                "findings": [
                    {
                        "topic": "Scalable Oversight",
                        "summary": "Scalable oversight techniques show promise for aligning large models [ev_1].",
                        "evidence_ids": ["ev_1"],
                        "confidence": 0.9,
                        "uncertainty": "Limited empirical validation on models >100B params",
                        "assumptions": ["Current scaling laws hold"]
                    }
                ],
                "conclusions": ["Scalable oversight is a viable path for AI alignment"],
                "limitations": ["Limited empirical validation on very large models"]
            }),
            model="gemini-2.5-pro",
            usage={"prompt_tokens": 500, "completion_tokens": 200, "total_tokens": 700},
        )
    )

    mock_router = MagicMock()
    mock_router.select_llm.return_value = mock_llm

    agent = ReportAgent()
    task = ResearchTask(
        id="task_report_1",
        job_id="job_1",
        type="report",
        objective="Generate report on AI safety",
        agent="report",
        inputs={
            "evidence": [
                {
                    "id": "ev_1",
                    "claim": "RLHF improves alignment on downstream tasks",
                    "supporting_text": "Our experiments show RLHF increases helpfulness by 40% and reduces harmful outputs by 60%.",
                    "confidence": 0.9,
                    "verification_status": "verified",
                    "verification_notes": "Consistent across multiple benchmarks"
                }
            ],
            "sources": [
                {
                    "id": "src_1",
                    "type": "web",
                    "url": "https://example.com/paper1",
                    "title": "RLHF for AI Alignment"
                }
            ],
            "question": "What are the current approaches to AI alignment?"
        }
    )

    context = AgentContext(
        research_job_id="job_1",
        task_id="task_report_1",
        request_id="req_1",
        tools={},
        memory=AgentMemory(),
        model_router=mock_router,
        config={},
    )

    result = await agent.run(task, context)

    assert result.success is True
    assert "title" in result.output
    assert "executive_summary" in result.output
    assert "methodology" in result.output
    assert "findings" in result.output
    assert len(result.output["findings"]) == 1
    assert result.output["findings"][0]["topic"] == "Scalable Oversight"
    assert "ev_1" in result.output["findings"][0]["evidence_ids"]
    assert "evidence_ids" in result.output
    assert "source_ids" in result.output
    assert "conclusions" in result.output
    assert "limitations" in result.output


@pytest.mark.asyncio
async def test_report_agent_empty_evidence():
    """ReportAgent handles empty/no verified evidence safely."""
    mock_router = MagicMock()
    agent = ReportAgent()
    task = ResearchTask(
        id="task_report_2",
        job_id="job_2",
        type="report",
        objective="Generate report on quantum computing",
        agent="report",
        inputs={
            "evidence": [],
            "sources": [],
            "question": "What is quantum computing?"
        }
    )

    context = AgentContext(
        research_job_id="job_2",
        task_id="task_report_2",
        request_id="req_2",
        tools={},
        memory=AgentMemory(),
        model_router=mock_router,
        config={},
    )

    result = await agent.run(task, context)

    assert result.success is True
    assert "title" in result.output
    assert "executive_summary" in result.output
    assert "methodology" in result.output
    assert result.output["findings"] == []
    assert result.metadata.get("empty_report") is True


@pytest.mark.asyncio
async def test_report_agent_preserves_citations():
    """ReportAgent preserves evidence citation references/IDs."""
    mock_llm = MagicMock()
    mock_llm.complete = AsyncMock(
        return_value=LLMResponse(
            content=json.dumps({
                "title": "Test Report",
                "executive_summary": "Summary",
                "methodology": "Methodology",
                "findings": [
                    {
                        "topic": "Finding 1",
                        "summary": "This finding cites ev_1 and ev_2 [ev_1, ev_2].",
                        "evidence_ids": ["ev_1", "ev_2"],
                        "confidence": 0.85
                    },
                    {
                        "topic": "Finding 2",
                        "summary": "This finding cites ev_3 [ev_3].",
                        "evidence_ids": ["ev_3"],
                        "confidence": 0.75
                    }
                ],
                "conclusions": ["Conclusion 1"],
                "limitations": ["Limitation 1"]
            }),
            model="test-model",
            usage={},
        )
    )

    mock_router = MagicMock()
    mock_router.select_llm.return_value = mock_llm

    agent = ReportAgent()
    task = ResearchTask(
        id="task_report_3",
        job_id="job_3",
        type="report",
        objective="Test citations",
        agent="report",
        inputs={
            "evidence": [
                {"id": "ev_1", "claim": "Claim 1", "supporting_text": "Text 1", "confidence": 0.9, "verification_status": "verified"},
                {"id": "ev_2", "claim": "Claim 2", "supporting_text": "Text 2", "confidence": 0.8, "verification_status": "verified"},
                {"id": "ev_3", "claim": "Claim 3", "supporting_text": "Text 3", "confidence": 0.7, "verification_status": "verified"},
            ],
            "sources": [],
            "question": "Test question"
        }
    )

    context = AgentContext(
        research_job_id="job_3",
        task_id="task_report_3",
        request_id="req_3",
        tools={},
        memory=AgentMemory(),
        model_router=mock_router,
        config={},
    )

    result = await agent.run(task, context)

    assert result.success is True
    # Check that all evidence IDs are preserved in output
    output_evidence_ids = result.output.get("evidence_ids", [])
    assert "ev_1" in output_evidence_ids
    assert "ev_2" in output_evidence_ids
    assert "ev_3" in output_evidence_ids
    # Check findings have evidence_ids
    for finding in result.output["findings"]:
        assert "evidence_ids" in finding
        assert len(finding["evidence_ids"]) > 0


@pytest.mark.asyncio
async def test_report_agent_handles_unverified_evidence():
    """ReportAgent does NOT synthesize findings from unverified/refuted/inconclusive evidence.
    
    When no verified/consensus/single_source evidence exists, the agent returns
    an empty report indicating no verified evidence was available.
    """
    mock_llm = MagicMock()
    mock_llm.complete = AsyncMock(
        return_value=LLMResponse(
            content=json.dumps({
                "title": "Test Report",
                "executive_summary": "Summary",
                "methodology": "Methodology",
                "findings": [],
                "conclusions": [],
                "limitations": []
            }),
        model="test-model",
        usage={},
    )
    )

    mock_router = MagicMock()
    mock_router.select_llm.return_value = mock_llm

    agent = ReportAgent()
    task = ResearchTask(
        id="task_report_4",
        job_id="job_4",
        type="report",
        objective="Test unverified evidence",
        agent="report",
        inputs={
            "evidence": [
                {"id": "ev_1", "claim": "Unverified claim", "supporting_text": "Unverified text", "confidence": 0.3, "verification_status": "unverified"},
                {"id": "ev_2", "claim": "Refuted claim", "supporting_text": "Refuted text", "confidence": 0.2, "verification_status": "refuted"},
                {"id": "ev_3", "claim": "Inconclusive claim", "supporting_text": "Inconclusive text", "confidence": 0.4, "verification_status": "inconclusive"},
            ],
            "sources": [],
            "question": "Test question"
        }
    )

    context = AgentContext(
        research_job_id="job_4",
        task_id="task_report_4",
        request_id="req_4",
        tools={},
        memory=AgentMemory(),
        model_router=mock_router,
        config={},
    )

    result = await agent.run(task, context)

    assert result.success is True
    # Should return empty report (no findings synthesized from unverified evidence)
    assert result.output["findings"] == []
    assert result.metadata.get("empty_report") is True
    # LLM should NOT have been called for synthesis
    mock_llm.complete.assert_not_awaited()
    # Empty report should indicate no verified evidence
    assert "No evidence" in result.output["executive_summary"] or "no verified evidence" in result.output["executive_summary"].lower()


@pytest.mark.asyncio
async def test_report_agent_llm_failure():
    """ReportAgent handles LLM failures gracefully."""
    mock_llm = MagicMock()
    mock_llm.complete = AsyncMock(side_effect=Exception("LLM API error"))

    mock_router = MagicMock()
    mock_router.select_llm.return_value = mock_llm

    agent = ReportAgent()
    task = ResearchTask(
        id="task_report_5",
        job_id="job_5",
        type="report",
        objective="Test LLM failure",
        agent="report",
        inputs={
            "evidence": [
                {"id": "ev_1", "claim": "Claim", "supporting_text": "Text", "confidence": 0.9, "verification_status": "verified"}
            ],
            "sources": [],
            "question": "Test question"
        }
    )

    context = AgentContext(
        research_job_id="job_5",
        task_id="task_report_5",
        request_id="req_5",
        tools={},
        memory=AgentMemory(),
        model_router=mock_router,
        config={},
    )

    result = await agent.run(task, context)

    assert result.success is False
    assert len(result.errors) > 0
    assert "Report generation failed" in result.errors[0]