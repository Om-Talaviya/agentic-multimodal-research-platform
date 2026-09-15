"""Tests for DocumentAnalysisAgent with hybrid knowledge retrieval (Phase 9)."""

import json
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
import pytest
from agents.base import AgentContext
from agents.research.document_agent import DocumentAnalysisAgent
from ai.schemas import LLMResponse
from research.models import ResearchTask


@pytest.mark.asyncio
async def test_document_agent_hybrid_knowledge_search():
    agent = DocumentAnalysisAgent()
    mock_context = MagicMock()
    mock_context.research_job_id = "job-456"
    mock_context.memory = MagicMock()

    # Mock knowledge_search tool
    mock_search_tool = MagicMock()
    mock_search_tool.execute = AsyncMock(return_value=[
        {
            "chunk_id": "chunk_abc",
            "document_id": "doc_xyz",
            "content": "PHA polymers undergo complete anaerobic digestion within 45 days.",
            "citation": "Doc: doc_xyz | Chunk #2",
            "score": 0.88,
        }
    ])
    mock_context.tools = {"knowledge_search": mock_search_tool}

    # Mock LLM analysis response
    llm_analysis_json = """{
        "findings": [
            {
                "claim": "PHA polymers degrade under anaerobic conditions within 45 days",
                "evidence": "PHA polymers undergo complete anaerobic digestion within 45 days",
                "confidence": 0.95,
                "section": "Chunk #2",
                "modality": "text"
            }
        ],
        "summary": "High anaerobic degradation rate for PHA"
    }"""
    mock_context.complete_llm = AsyncMock(return_value=LLMResponse(model="test-model", content=llm_analysis_json))

    task = ResearchTask(
        id=str(uuid4()),
        job_id="job-456",
        type="document_analysis",
        objective="Assess anaerobic degradation rates of bioplastics",
        agent="document_analysis",
        inputs={"query": "anaerobic digestion bioplastics"},
    )

    result = await agent.run(task, mock_context)

    assert result.success is True
    assert mock_search_tool.execute.await_count == 1
    assert len(result.output["evidence"]) == 1
    assert result.output["evidence"][0].claim == "PHA polymers degrade under anaerobic conditions within 45 days"
    assert result.output["evidence"][0].confidence == 0.95
