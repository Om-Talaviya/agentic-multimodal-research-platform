"""Tests for knowledge graph agent tools."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from tools.definitions.graph import (
    QueryKnowledgeGraphTool,
    ExtractGraphTripletsTool,
    FindRelationPathTool,
)
from research.graph.models import (
    GraphExtractionResult,
    GraphTriplet,
    GraphPathResult,
    GraphPathStep,
    EntityType,
    RelationType,
)


@pytest.fixture
def mock_graph_engine():
    engine = MagicMock()
    engine.get_graph_augmented_context = AsyncMock()
    engine.extract_triplets_from_text = AsyncMock()
    engine.find_path_between_entities = AsyncMock()
    return engine


@pytest.mark.asyncio
async def test_query_knowledge_graph_tool(mock_graph_engine):
    mock_graph_engine.get_graph_augmented_context.return_value = (
        "Entities:\n- Quantum Computing (CONCEPT)\n\nRelations:\n- Quantum Computing --[RELATES_TO]--> Cryptography",
        [],
    )
    
    tool = QueryKnowledgeGraphTool(graph_engine=mock_graph_engine)
    result = await tool.execute(query="Quantum Computing", max_hops=2)
    
    assert result["success"] is True
    assert "Quantum Computing" in result["context"]
    mock_graph_engine.get_graph_augmented_context.assert_awaited_once_with(
        query="Quantum Computing",
        user_id=None,
        max_hops=2,
    )


@pytest.mark.asyncio
async def test_extract_graph_triplets_tool(mock_graph_engine):
    triplet = GraphTriplet(
        source="Alice",
        source_type="PERSON",
        relation="DEVELOPED_BY",
        target="DeepMind",
        target_type="ORGANIZATION",
        description="Alice works at DeepMind",
        confidence=0.95,
    )
    mock_graph_engine.extract_triplets_from_text.return_value = GraphExtractionResult(
        entities_count=2,
        relations_count=1,
        triplets=[triplet],
        extracted_entities=["Alice", "DeepMind"],
    )
    
    tool = ExtractGraphTripletsTool(graph_engine=mock_graph_engine)
    result = await tool.execute(text="Alice joined DeepMind as a researcher.")
    
    assert result["success"] is True
    assert result["data"]["entities_count"] == 2
    assert result["data"]["relations_count"] == 1
    assert len(result["data"]["triplets"]) == 1
    assert result["data"]["triplets"][0]["source"] == "Alice"
    assert result["data"]["triplets"][0]["target"] == "DeepMind"


@pytest.mark.asyncio
async def test_find_relation_path_tool(mock_graph_engine):
    mock_graph_engine.find_path_between_entities.return_value = GraphPathResult(
        source_entity="Transformer",
        target_entity="GPT-4",
        path_found=True,
        hop_count=2,
        steps=[
            GraphPathStep(
                from_id="e1",
                to_id="e2",
                relation_id="r1",
                relation_type="DERIVED_FROM",
                description="Transformer derived from Attention Mechanism",
                direction="OUTGOING",
            ),
            GraphPathStep(
                from_id="e2",
                to_id="e3",
                relation_id="r2",
                relation_type="RELATES_TO",
                description="Attention Mechanism relates to GPT-4",
                direction="OUTGOING",
            ),
        ],
        summary="Transformer -> Attention Mechanism -> GPT-4",
    )
    
    tool = FindRelationPathTool(graph_engine=mock_graph_engine)
    result = await tool.execute(source_entity="Transformer", target_entity="GPT-4", max_depth=3)
    
    assert result["success"] is True
    assert result["data"]["path_found"] is True
    assert result["data"]["hop_count"] == 2
    assert len(result["data"]["steps"]) == 2
