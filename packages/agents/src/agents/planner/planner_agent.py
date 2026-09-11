"""Planner agent - creates research plans from requests."""

import json
from agents.base import Agent, AgentContext, AgentResult
from research.models import ResearchTask, ResearchPlan, ResearchStep
from ai.schemas import LLMRequest, LLMMessage
from ai.providers.router import ModelRouter
from ai.schemas import ModelCapabilities
from shared.logging import get_logger

logger = get_logger(__name__)


class PlannerAgent(Agent):
    """Decomposes research requests into executable plans, leveraging available knowledge base context."""
    
    name = "planner"
    description = "Creates research plans from user requests with knowledge base awareness"
    capabilities = {"planning", "task_decomposition", "knowledge_routing"}
    
    SYSTEM_PROMPT = """You are an expert research planner for an AI Research Operating System.
Given a research question and any available private knowledge base context, create a structured
research plan as a JSON object with the following schema:
{
    "objective": "Clear statement of research goal",
    "steps": [
        {
            "id": "step_1",
            "name": "Descriptive step title",
            "description": "What this step accomplishes",
            "agent": "web_research|document_analysis|synthesis|report",
            "inputs": {
                "query": "search query or focus topic",
                "document_ids": ["optional_doc_id_1"]
            },
            "depends_on": [],
            "priority": 1
        }
    ],
    "expected_outputs": ["executive_summary", "key_findings", "evidence_matrix", "conclusions"]
}

Available agents:
- document_analysis: Ingest and analyze uploaded documents, PDFs with tables, and private knowledge base chunks.
- web_research: Search and retrieve live external web sources.
- synthesis: Combine, cross-reference, and compare findings from multiple modalities and sources.
- report: Synthesize final intelligence report with citations.

Planning Guidelines:
1. If "Available Private Knowledge Base" or uploaded documents are provided, ALWAYS schedule a "document_analysis" step to extract local domain findings. Pass the relevant document_ids or search queries in inputs.
2. Schedule "web_research" steps for external web coverage. Steps without mutual dependencies can run in parallel (e.g. document_analysis and web_research).
3. Conclude with a "report" step that depends on all upstream investigation steps.
4. Keep the plan focused and create 3-5 high-impact steps.
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
                    temperature=0.3,
                    json_mode=True,
                ),
                task="planning",
            )
            
            plan_data = json.loads(response.content)
            plan = ResearchPlan(**plan_data)
            
            logger.info("Plan created", job_id=context.research_job_id, steps=len(plan.steps))
            
            return AgentResult(
                success=True,
                output=plan,
                metadata={"model": response.model, "tokens": response.usage},
            )
        except Exception as e:
            logger.error("Planning failed", error=str(e))
            return AgentResult(
                success=False,
                errors=[f"Failed to create plan: {e}"],
            )