"""Unit tests for Phase 11: Advanced Research Planning, Query Trees, and Dynamic Replanning."""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock
from agents.planner.planner_agent import PlannerAgent
from agents.base import AgentContext, AgentMemory
from research.models import (
    ResearchTask,
    ResearchPlan,
    ResearchStep,
    QueryTreeNode,
    InferredScope,
    Evidence,
    Contradiction,
)
from ai.schemas import LLMResponse, TokenUsage


@pytest.fixture
def mock_context():
    ctx = MagicMock(spec=AgentContext)
    ctx.research_job_id = "job-p11-test"
    ctx.task_id = "task-p11-plan"
    ctx.request_id = "req-p11-test"
    ctx.user_id = "user-123"
    ctx.memory = AgentMemory()
    return ctx


@pytest.mark.asyncio
async def test_planner_hierarchical_query_tree_generation(mock_context):
    """Verify PlannerAgent generates structured query tree, ambiguity score, and inferred scope."""
    planner = PlannerAgent()
    
    mock_plan_payload = {
        "objective": "Analyze the commercialization timeline of solid-state EV batteries",
        "ambiguity_score": 0.25,
        "inferred_scope": {
            "domain": "materials_science",
            "time_horizon": "2025-2035",
            "geography": "Global",
            "key_entities": ["QuantumScape", "Solid Power", "Toyota", "Solid-State Battery"],
            "constraints": ["focus on energy density and manufacturing scale"]
        },
        "plan_explanation": "Strategic decomposition into material chemistry, cost economics, and OEM testing.",
        "query_tree": {
            "id": "root_node",
            "parent_id": None,
            "question": "Will solid-state batteries surpass lithium-ion in commercial EVs by 2030?",
            "rationale": "High-level research objective",
            "domain_focus": "materials_science",
            "depth": 0,
            "assigned_agent": "synthesis",
            "subqueries": [
                {
                    "id": "node_tech",
                    "parent_id": "root_node",
                    "question": "What are the latest laboratory energy density and dendritic suppression benchmarks?",
                    "rationale": "Extract core physical viability metrics",
                    "domain_focus": "technical",
                    "depth": 1,
                    "assigned_agent": "document_analysis",
                    "subqueries": [
                        {
                            "id": "node_tech_detail",
                            "parent_id": "node_tech",
                            "question": "Compare sulfide vs oxide electrolyte ionic conductivity rates",
                            "rationale": "Microscopic performance metrics",
                            "domain_focus": "technical",
                            "depth": 2,
                            "assigned_agent": "document_analysis",
                            "subqueries": []
                        }
                    ]
                },
                {
                    "id": "node_market",
                    "parent_id": "root_node",
                    "question": "What are OEM pilot vehicle testing roadmaps and projected cost per kWh?",
                    "rationale": "Evaluate industrial scaling feasibility",
                    "domain_focus": "market",
                    "depth": 1,
                    "assigned_agent": "web_research",
                    "subqueries": []
                }
            ]
        },
        "steps": [
            {
                "id": "step_1",
                "name": "Analyze Laboratory Benchmarks in Research Papers",
                "description": "Extract ionic conductivity and cycle life data from uploaded documents",
                "agent": "document_analysis",
                "inputs": {"query": "solid-state electrolyte ionic conductivity cycle life"},
                "depends_on": [],
                "priority": 1,
                "parent_id": "node_tech",
                "depth": 1,
                "is_dynamic": False
            },
            {
                "id": "step_2",
                "name": "Survey OEM Commercial Roadmaps",
                "description": "Retrieve live automotive announcements and factory pilot milestones",
                "agent": "web_research",
                "inputs": {"query": "solid-state battery automotive OEM commercial roadmap 2025 2030"},
                "depends_on": [],
                "priority": 1,
                "parent_id": "node_market",
                "depth": 1,
                "is_dynamic": False
            },
            {
                "id": "step_3",
                "name": "Cross-Verify and Synthesize Evidence",
                "description": "Synthesize findings and audit contradictions",
                "agent": "synthesis",
                "inputs": {},
                "depends_on": ["step_1", "step_2"],
                "priority": 2,
                "parent_id": "root_node",
                "depth": 0,
                "is_dynamic": False
            },
            {
                "id": "step_4",
                "name": "Generate Intelligence Report",
                "description": "Compile verified dossier with citations",
                "agent": "report",
                "inputs": {},
                "depends_on": ["step_3"],
                "priority": 3,
                "parent_id": "root_node",
                "depth": 0,
                "is_dynamic": False
            }
        ],
        "expected_outputs": ["executive_summary", "key_findings", "evidence_matrix", "contradictions_matrix", "conclusions"]
    }

    mock_context.complete_llm = AsyncMock(
        return_value=LLMResponse(
            content=json.dumps(mock_plan_payload),
            model="gemini-2.0-flash",
            usage=TokenUsage(prompt_tokens=250, completion_tokens=400, total_tokens=650),
        )
    )

    task = ResearchTask(
        id="task-p11-run",
        job_id="job-p11-test",
        type="planning",
        objective="Analyze the commercialization timeline of solid-state EV batteries",
        agent="planner",
    )

    result = await planner.run(task, mock_context)

    assert result.success is True
    plan: ResearchPlan = result.output
    assert isinstance(plan, ResearchPlan)
    assert plan.ambiguity_score == 0.25
    assert plan.inferred_scope is not None
    assert plan.inferred_scope.domain == "materials_science"
    assert len(plan.steps) == 4
    assert plan.query_tree is not None
    assert plan.query_tree.question == "Will solid-state batteries surpass lithium-ion in commercial EVs by 2030?"
    assert len(plan.query_tree.subqueries) == 2
    assert plan.query_tree.subqueries[0].subqueries[0].id == "node_tech_detail"


@pytest.mark.asyncio
async def test_planner_adaptive_dynamic_replanning(mock_context):
    """Verify PlannerAgent.replan() spawns targeted subtasks to resolve contradictory or low-confidence findings."""
    planner = PlannerAgent()

    mock_replan_payload = {
        "plan_explanation": "Contradiction detected between Paper A (450 Wh/kg) and OEM Report B (280 Wh/kg). Spawning targeted verification subtask.",
        "spawned_steps": [
            {
                "id": "step_dyn_1",
                "name": "Investigate Discrepancy in Pack-Level vs Cell-Level Energy Density",
                "description": "Execute targeted search to reconcile 450 Wh/kg cell level vs 280 Wh/kg pack level reporting",
                "agent": "web_research",
                "inputs": {"query": "QuantumScape cell level vs pack level energy density Wh/kg 2026"},
                "depends_on": [],
                "priority": 1,
                "parent_id": "root_node",
                "depth": 1,
                "is_dynamic": True
            }
        ]
    }

    mock_context.complete_llm = AsyncMock(
        return_value=LLMResponse(
            content=json.dumps(mock_replan_payload),
            model="gemini-2.0-flash",
            usage=TokenUsage(prompt_tokens=300, completion_tokens=150, total_tokens=450),
        )
    )

    current_plan = ResearchPlan(
        objective="Analyze solid-state battery energy density",
        steps=[],
        inferred_scope=InferredScope(domain="materials_science"),
    )

    evidence_list = [
        Evidence(
            id="ev-1",
            source_id="src-1",
            claim="Solid-state cells achieve 450 Wh/kg under lab conditions",
            supporting_text="Lab testing showed 450 Wh/kg",
            confidence=0.9,
            verification_status="verified",
        ),
        Evidence(
            id="ev-2",
            source_id="src-2",
            claim="Commercial EV battery packs only deliver 280 Wh/kg",
            supporting_text="Field tests yielded 280 Wh/kg",
            confidence=0.6,
            verification_status="disputed",
        ),
    ]

    contradictions = [
        Contradiction(
            id="c-1",
            topic="Energy Density",
            claim_a="450 Wh/kg under lab conditions",
            source_a="Paper A",
            claim_b="280 Wh/kg in commercial packs",
            source_b="OEM Report B",
            conflict_type="numerical_discrepancy",
            explanation="Discrepancy between cell-level and pack-level metrics",
            severity="high",
        )
    ]

    replan_result = await planner.replan(
        current_plan=current_plan,
        evidence=evidence_list,
        contradictions=contradictions,
        context=mock_context,
    )

    assert replan_result.success is True
    assert "spawned_steps" in replan_result.output
    spawned_steps = replan_result.output["spawned_steps"]
    assert len(spawned_steps) == 1
    assert spawned_steps[0].id == "step_dyn_1"
    assert spawned_steps[0].is_dynamic is True
    assert "Discrepancy" in spawned_steps[0].name
