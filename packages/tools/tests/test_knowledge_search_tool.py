"""Unit tests for KnowledgeSearchTool."""

from unittest.mock import AsyncMock, MagicMock
import pytest
from retrieval.retriever import GroundedEvidence
from tools.definitions.knowledge_search import KnowledgeSearchTool


@pytest.mark.asyncio
async def test_knowledge_search_tool_execution():
    mock_retriever = MagicMock()
    mock_retriever.retrieve = AsyncMock(
        return_value=[
            GroundedEvidence(
                chunk_id="chunk_101",
                content="Transformer attention enables multimodal alignment.",
                score=0.95,
                document_id="doc_abc",
                modality="text",
                citation="Doc: doc_abc | Chunk #0",
            )
        ]
    )

    tool = KnowledgeSearchTool(retriever=mock_retriever)
    assert tool.schema.name == "knowledge_search"

    results = await tool.execute(query="multimodal alignment", top_k=3, document_id="doc_abc")

    assert len(results) == 1
    assert results[0]["chunk_id"] == "chunk_101"
    assert results[0]["score"] == 0.95
    assert results[0]["citation"] == "Doc: doc_abc | Chunk #0"

    mock_retriever.retrieve.assert_called_once_with(
        query="multimodal alignment",
        top_k=3,
        filter={"document_id": "doc_abc"},
    )
