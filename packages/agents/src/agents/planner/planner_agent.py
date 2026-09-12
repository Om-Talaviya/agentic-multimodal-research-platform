"""Planner agent - creates hierarchical research plans, query trees, and dynamic replans from requests."""

import json
from typing import List, Dict, Any, Optional
from agents.base import Agent, AgentContext, AgentResult
from research.models import (
    ResearchTask,
    ResearchPlan,
    ResearchStep,
    QueryTreeNode,
    InferredScope,
    Evidence,
    Contradiction,
)
from ai.schemas import LLMRequest, LLMMessage
from shared.logging import get_logger

logger = get_logger(__name__)


class PlannerAgent(Agent):
    """Advanced strategic planner: decomposes inquiries into hierarchical query trees, measures ambiguity, and performs closed-loop replanning."""
    
    name = "planner"
    description = "Creates hierarchical research plans with query trees, ambiguity scoring, and adaptive dynamic replanning"
    capabilities = {
        "planning",
        "task_decomposition",
        "query_tree_generation",
        "ambiguity_scoring",
        "dynamic_replanning",
        "knowledge_routing",
    }
    
    SYSTEM_PROMPT = """You are the Lead Research Strategist for an autonomous AI Research Operating System.
Your job is to transform a research inquiry into a deeply structured, hierarchical strategic research plan.

Analyze the question for clarity and ambiguity (score 0.0 for crystal clear to 1.0 for vague/underspecified).
Infer key scope dimensions (domain, time horizon, geography, key entities, constraints).
Deconstruct the inquiry into a hierarchical Query Tree (Root -> 2-4 Thematic Subinquiries -> 1-2 Specific Granular Subquestions).
Compile the tree into executable DAG Research Steps with dependencies.

Respond with a strictly formatted JSON object adhering to this schema:
{
    "objective": "Clear, precise statement of the core research objective",
    "ambiguity_score": 0.2,
    "inferred_scope": {
        "domain": "e.g. materials_science, renewable_energy, macroeconomics, healthcare",
        "time_horizon": "e.g. 2025-2035, past 5 years, or immediate",
        "geography": "e.g. Global, US/EU, Asia-Pacific",
        "key_entities": ["Entity A", "Entity B"],
        "constraints": ["Constraint 1", "Constraint 2"]
    },
    "plan_explanation": "Strategic justification for this investigation approach",
    "query_tree": {
        "id": "root_node",
        "parent_id": null,
        "question": "Main overarching research question",
        "rationale": "High-level goal",
        "domain_focus": "general",
        "depth": 0,
        "assigned_agent": "synthesis",
        "subqueries": [
            {
                "id": "node_1",
                "parent_id": "root_node",
                "question": "Sub-inquiry regarding technical feasibility or core mechanisms",
                "rationale": "Investigates baseline technical claims and benchmarks",
                "domain_focus": "technical",
                "depth": 1,
                "assigned_agent": "document_analysis",
                "subqueries": [
                    {
                        "id": "node_1_1",
                        "parent_id": "node_1",
                        "question": "Granular question targeting specific metrics or data",
                        "rationale": "Extracts quantitative empirical figures",
                        "domain_focus": "technical",
                        "depth": 2,
                        "assigned_agent": "document_analysis",
                        "subqueries": []
                    }
                ]
            },
            {
                "id": "node_2",
                "parent_id": "root_node",
                "question": "Sub-inquiry regarding external market, regulatory, or empirical context",
                "rationale": "Surveys industry adoption and public landscape",
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
            "name": "Descriptive step title",
            "description": "Specific action and target data to extract",
            "agent": "document_analysis|web_research|synthesis|report",
            "inputs": {
                "query": "search query or focus topic",
                "document_ids": []
            },
            "depends_on": [],
            "priority": 1,
            "parent_id": "node_1",
            "depth": 1,
            "is_dynamic": false
        },
        {
            "id": "step_2",
            "name": "Synthesize and Audit Evidence",
            "description": "Combine findings, reconcile contradictions, and verify confidence",
            "agent": "synthesis",
            "inputs": {},
            "depends_on": ["step_1"],
            "priority": 2,
            "parent_id": "root_node",
            "depth": 0,
            "is_dynamic": false
        },
        {
            "id": "step_3",
            "name": "Final Intelligence Report Synthesis",
            "description": "Compile verified evidence, citation coordinates, and contradictions into final dossier",
            "agent": "report",
            "inputs": {},
            "depends_on": ["step_2"],
            "priority": 3,
            "parent_id": "root_node",
            "depth": 0,
            "is_dynamic": false
        }
    ],
    "expected_outputs": ["executive_summary", "key_findings", "evidence_matrix", "contradictions_matrix", "conclusions"]
}

Planning Guidelines:
1. If "Available Private Knowledge Base" or attached documents exist, ALWAYS assign "document_analysis" steps to inspect internal files before or in parallel with external web search.
2. Ensure upstream investigation steps have empty depends_on so they run in parallel.
3. The final "report" step MUST depend on all preceding investigation/synthesis steps.
4. Keep the plan rigorous, creating 3 to 6 high-impact executable steps.
"""

    REPLAN_PROMPT = """You are the Lead Research Strategist directing an autonomous deep research recursive loop (Iteration #{iteration_index}).
The Critic Agent evaluated collected findings and highlighted contradictions, evidentiary gaps, and unresolved hypotheses.

Original Objective: {objective}
Current Inferred Scope: {scope}
Targeted Hypotheses to Validate:
{hypotheses}

Unresolved Evidentiary Gaps:
{unresolved_gaps}

Critic Gap Queries:
{gap_queries}

Identified Contradictions:
{contradictions}

Low-Confidence or Unverified Claims:
{low_confidence_evidence}

Generate a delta replanning JSON object with targeted follow-up steps to resolve the contradictions, validate hypotheses, and close evidentiary gaps:
{{
    "plan_explanation": "Rationale for dynamic replanning in iteration {iteration_index}",
    "spawned_steps": [
        {{
            "id": "step_dynamic_1",
            "name": "Targeted deep-dive step title",
            "description": "Specific investigation to resolve conflicting claim or test hypothesis",
            "agent": "web_research|document_analysis|synthesis",
            "inputs": {{
                "query": "laser-focused search query",
                "document_ids": []
            }},
            "depends_on": [],
            "priority": 1,
            "parent_id": "root_node",
            "depth": 1,
            "is_dynamic": true
        }}
    ]
}}
"""

    async def run(self, task: ResearchTask, context: AgentContext) -> AgentResult:
        knowledge_summary = task.context.get("available_knowledge") or task.context.get("knowledge_summary") or ""
        doc_ids = task.context.get("document_ids") or []
        
        prompt_parts = [f"Research Request: {task.objective}"]
        
        if task.context:
            context_meta = {k: v for k, v in task.context.items() if k not in ("available_knowledge", "knowledge_summary")}
            if context_meta:
                prompt_parts.append(f"Context Parameters: {context_meta}")
                
        if knowledge_summary:
            prompt_parts.append(f"Available Private Knowledge Base:\n{knowledge_summary}")
        elif doc_ids:
            prompt_parts.append(f"Available Attached Documents: {doc_ids}")
            
        prompt = "\n\n".join(prompt_parts)
        
        try:
            response = await context.complete_llm(
                LLMRequest(
                    messages=[
                        LLMMessage(role="system", content=self.SYSTEM_PROMPT),
                        LLMMessage(role="user", content=prompt),
                    ],
                    temperature=0.2,
                    json_mode=True,
                ),
                task="planning",
            )
            
            plan_data = json.loads(response.content)
            plan = ResearchPlan(**plan_data)
            
            logger.info(
                "Hierarchical plan created",
                job_id=context.research_job_id,
                steps=len(plan.steps),
                ambiguity=plan.ambiguity_score,
                domain=plan.inferred_scope.domain if plan.inferred_scope else "general",
            )
            
            return AgentResult(
                success=True,
                output=plan,
                metadata={
                    "model": response.model,
                    "tokens": response.usage,
                    "ambiguity_score": plan.ambiguity_score,
                    "query_tree": plan.query_tree.model_dump() if plan.query_tree else None,
                },
            )
        except Exception as e:
            logger.error("Planning failed", error=str(e))
            return AgentResult(
                success=False,
                errors=[f"Failed to create hierarchical plan: {e}"],
            )

    async def replan(
        self,
        current_plan: ResearchPlan,
        evidence: List[Evidence],
        contradictions: List[Contradiction],
        context: AgentContext,
        unresolved_gaps: Optional[List[str]] = None,
        gap_queries: Optional[List[str]] = None,
        hypotheses: Optional[List[str]] = None,
        iteration_index: int = 1,
    ) -> AgentResult:
        """Dynamically generate targeted follow-up tasks to resolve contradictions and fill low-confidence gaps."""
        low_conf = [e for e in evidence if e.confidence < 0.65 or e.verification_status != "verified"]
        
        contradictions_text = "\n".join(
            [f"- [{c.conflict_type}] Topic '{c.topic}': Claim A ('{c.claim_a}') vs Claim B ('{c.claim_b}'). Explanation: {c.explanation}" for c in contradictions]
        ) or "None"
        
        low_conf_text = "\n".join(
            [f"- Claim: '{e.claim}' (Confidence: {e.confidence:.2f}, Status: {e.verification_status})" for e in low_conf[:5]]
        ) or "None"

        gaps_text = "\n".join([f"- {g}" for g in (unresolved_gaps or [])]) or "None"
        gap_queries_text = "\n".join([f"- {q}" for q in (gap_queries or [])]) or "None"
        hypotheses_text = "\n".join([f"- {h}" for h in (hypotheses or [])]) or "None"
        
        prompt = self.REPLAN_PROMPT.format(
            iteration_index=iteration_index,
            objective=current_plan.objective,
            scope=current_plan.inferred_scope.model_dump_json() if current_plan.inferred_scope else "N/A",
            hypotheses=hypotheses_text,
            unresolved_gaps=gaps_text,
            gap_queries=gap_queries_text,
            contradictions=contradictions_text,
            low_confidence_evidence=low_conf_text,
        )
        
        try:
            response = await context.complete_llm(
                LLMRequest(
                    messages=[
                        LLMMessage(role="system", content=self.SYSTEM_PROMPT),
                        LLMMessage(role="user", content=prompt),
                    ],
                    temperature=0.2,
                    json_mode=True,
                ),
                task="planning",
            )
            
            replan_data = json.loads(response.content)
            spawned_steps_raw = replan_data.get("spawned_steps", [])
            spawned_steps = [ResearchStep(**s) for s in spawned_steps_raw]
            
            # If LLM didn't spawn any steps but we have gap queries, construct fallback steps
            if not spawned_steps and gap_queries:
                for idx, gq in enumerate(gap_queries[:3]):
                    spawned_steps.append(
                        ResearchStep(
                            id=f"step_dynamic_gap_{iteration_index}_{idx+1}",
                            name=f"Investigate gap: {gq[:40]}",
                            description=f"Investigate missing evidence: {gq}",
                            agent="web_research",
                            inputs={"query": gq},
                            priority=1,
                            depth=iteration_index,
                            is_dynamic=True,
                        )
                    )

            logger.info(
                "Dynamic replan executed",
                job_id=context.research_job_id,
                iteration=iteration_index,
                spawned_steps=len(spawned_steps),
                reason=replan_data.get("plan_explanation"),
            )
            
            return AgentResult(
                success=True,
                output={
                    "plan_explanation": replan_data.get("plan_explanation", f"Dynamic replan for iteration #{iteration_index}"),
                    "spawned_steps": spawned_steps,
                },
                metadata={"model": response.model, "tokens": response.usage},
            )
        except Exception as e:
            logger.error("Replanning failed", error=str(e))
            return AgentResult(
                success=False,
                errors=[f"Failed to generate dynamic replan: {e}"],
            )