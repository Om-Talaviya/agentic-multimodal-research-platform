"""Unit tests for DocumentAnalysisAgent multimodal handoff."""

import json
from unittest.mock import AsyncMock, MagicMock
import pytest
from agents.base import AgentContext
from agents.memory import AgentMemory
from agents.research.document_agent import DocumentAnalysisAgent
from research.models import ResearchTask
from ai.schemas import LLMResponse


@pytest.mark.asyncio
async def test_document_analysis_multimodal_extraction():
    mock_doc_tool = MagicMock()
    mock_doc_tool.execute = AsyncMock(
        return_value=(
            "=== Document: paper.pdf (Chunks: 2) ===\n"
            "--- Chunk 0 [Type: table] ---\n"
            "| Model | Accuracy | Latency |\n| GPT-4 | 92.5% | 450ms |\n\n"
            "--- Chunk 1 [Type: image_description] ---\n"
            "[Vision OCR Diagram]: Figure 2 shows the dual-encoder attention architecture."
        )
    )

    mock_llm = MagicMock()
    mock_llm.complete = AsyncMock(
        return_value=LLMResponse(
            content=json.dumps({
                "findings": [
                    {
                        "claim": "GPT-4 achieved 92.5% accuracy with 450ms latency.",
                        "evidence": "Table data: | GPT-4 | 92.5% | 450ms |",
                        "confidence": 0.95,
                        "modality": "table",
                    },
                    {
                        "claim": "Figure 2 details dual-encoder attention.",
                        "evidence": "Vision OCR Diagram description",
                        "confidence": 0.88,
                        "modality": "image",
                    },
                ],
                "summary": "Document presents benchmark table and architecture diagram."
            }),
            model="gemini-2.5-pro",
            usage={"total_tokens": 350},
        )
    )

    mock_router = MagicMock()
    mock_router.select_llm.return_value = mock_llm

    agent = DocumentAnalysisAgent()
    task = ResearchTask(
        id="task_doc_1",
        job_id="job_1",
        type="document_analysis",
        objective="Extract model performance benchmarks and architecture details",
        agent="document_analysis",
        inputs={"document_ids": ["doc_uuid_123"]},
    )

    context = AgentContext(
        research_job_id="job_1",
        task_id="task_doc_1",
        request_id="req_1",
        tools={"document_read": mock_doc_tool},
        memory=AgentMemory(),
        model_router=mock_router,
        config={},
    )

    result = await agent.run(task, context)

    assert result.success is True
    assert len(result.evidence) == 2
    assert "92.5%" in result.evidence[0].claim
    assert result.metadata["documents_processed"] == 1
    assert context.memory.get_long_term("doc_doc_uuid_123_findings") is not None


@pytest.mark.asyncio
async def test_document_analysis_empty_doc_ids():
    mock_router = MagicMock()
    agent = DocumentAnalysisAgent()
    task = ResearchTask(
        id="task_doc_2",
        job_id="job_2",
        type="document_analysis",
        objective="Analyze documents",
        agent="document_analysis",
        inputs={"document_ids": []},
    )

    context = AgentContext(
        research_job_id="job_2",
        task_id="task_doc_2",
        request_id="req_2",
        tools={"document_read": MagicMock()},
        memory=AgentMemory(),
        model_router=mock_router,
        config={},
    )

    result = await agent.run(task, context)
    assert result.success is True
    assert len(result.evidence) == 0
    assert result.metadata["documents_processed"] == 0
