"""Tests for PlannerAgent and ResearchPipeline knowledge base integration (Phase 9)."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
import pytest
from agents.base import AgentContext, AgentResult
from agents.planner.planner_agent import PlannerAgent
from ai.schemas import LLMResponse
from research.models import ResearchJob, ResearchRequest, ResearchPlan, ResearchStep
from research.pipeline import ResearchPipeline
from retrieval.retriever import GroundedEvidence


@pytest.mark.asyncio
async def test_planner_agent_with_knowledge_summary():
    planner = PlannerAgent()
    mock_context = MagicMock()

    # Mock complete_llm returning structured JSON plan with document_analysis step
    plan_json = """{
        "objective": "Evaluate solid-state batteries",
        "steps": [
            {
                "id": "step_1",
                "name": "Analyze local battery research paper",
                "description": "Extract energy density findings from uploaded document",
                "agent": "document_analysis",
                "inputs": {"document_ids": ["doc_battery_01"]},
                "depends_on": [],
                "priority": 2
            },
            {
                "id": "step_2",
                "name": "Search latest commercial battery developments",
                "description": "Web search for 2026 solid-state announcements",
                "agent": "web_research",
                "inputs": {"query": "solid-state batteries commercial announcements 2026"},
                "depends_on": [],
                "priority": 1
            },
            {
                "id": "step_3",
                "name": "Synthesize report",
                "description": "Synthesize findings into final dossier",
                "agent": "report",
                "inputs": {},
                "depends_on": ["step_1", "step_2"],
                "priority": 3
            }
        ],
        "expected_outputs": ["executive_summary", "key_findings", "evidence_matrix"]
    }"""
    mock_context.complete_llm = AsyncMock(return_value=LLMResponse(model="test-model", content=plan_json, usage={"tokens": 100}))
    mock_context.research_job_id = "job-123"

    mock_task = MagicMock()
    mock_task.objective = "Evaluate solid-state battery feasibility"
    mock_task.context = {
        "available_knowledge": "- [Doc: doc_battery_01 | Page 3]: Silicon anode achieves 3500 mAh/g",
        "document_ids": ["doc_battery_01"],
    }

    result = await planner.run(mock_task, mock_context)

    assert result.success is True
    plan = result.output
    assert isinstance(plan, ResearchPlan)
    assert len(plan.steps) == 3
    agents_planned = [s.agent for s in plan.steps]
    assert "document_analysis" in agents_planned
    assert "web_research" in agents_planned
    assert "report" in agents_planned


@pytest.mark.asyncio
async def test_research_pipeline_queries_retriever_during_planning():
    mock_orchestrator = MagicMock()
    mock_orchestrator.create_context = MagicMock()
    mock_agent_reg = MagicMock()
    mock_tool_reg = MagicMock()
    mock_router = MagicMock()
    mock_event_bus = MagicMock()
    mock_event_bus.publish = AsyncMock()

    mock_retriever = MagicMock()
    mock_retriever.retrieve = AsyncMock(return_value=[
        GroundedEvidence(
            chunk_id="c_1",
            content="Biodegradable PLA degradation in marine environments is 18%",
            score=0.92,
            document_id="doc_marine_01",
            citation="Doc: doc_marine_01 | Page 12",
        )
    ])

    pipeline = ResearchPipeline(
        orchestrator=mock_orchestrator,
        agent_registry=mock_agent_reg,
        tool_registry=mock_tool_reg,
        model_router=mock_router,
        event_bus=mock_event_bus,
        retriever=mock_retriever,
    )

    job = ResearchJob(
        id=str(uuid4()),
        request_id=str(uuid4()),
        question="What is the degradation rate of PLA packaging in seawater?",
        objective="Analyze PLA degradation rate in seawater",
    )

    # Mock PlannerAgent run
    plan_json = """{
        "objective": "Analyze PLA degradation rate in seawater",
        "steps": [
            {
                "id": "step_1",
                "name": "Analyze Marine PLA Report",
                "description": "Extract degradation stats from doc_marine_01",
                "agent": "document_analysis",
                "inputs": {"document_ids": ["doc_marine_01"]},
                "depends_on": [],
                "priority": 1
            }
        ],
        "expected_outputs": ["key_findings"]
    }"""
    mock_context = MagicMock()
    mock_context.complete_llm = AsyncMock(return_value=LLMResponse(model="test-model", content=plan_json))
    mock_orchestrator.create_context.return_value = mock_context

    plan = await pipeline.run_planning(job)

    assert mock_retriever.retrieve.await_count == 1
    assert len(plan.steps) == 1
    assert plan.steps[0].agent == "document_analysis"
