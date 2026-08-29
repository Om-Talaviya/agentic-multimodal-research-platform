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
    """Decomposes research requests into executable plans."""
    
    name = "planner"
    description = "Creates research plans from user requests"
    capabilities = {"planning", "task_decomposition"}
    
    SYSTEM_PROMPT = """You are a research planner. Given a research question, create a structured
    research plan as a JSON object with the following schema:
    {
        "objective": "Clear statement of research goal",
        "steps": [
            {
                "id": "step_1",
                "name": "Descriptive name",
                "description": "What this step accomplishes",
                "agent": "agent_name",
                "inputs": {"key": "value"},
                "depends_on": ["step_id"],
                "priority": 1
            }
        ],
        "expected_outputs": ["output_type1", "output_type2"]
    }
    
    Available agents: 
    - web_research: Search and fetch web content
    - document_analysis: Analyze uploaded documents
    - synthesis: Combine findings from multiple sources
    - report: Generate final report
    
    Create 3-5 steps. Steps without dependencies run in parallel.
    """
    
    async def run(self, task: ResearchTask, context: AgentContext) -> AgentResult:
        router: ModelRouter = context.model_router
        llm = router.select_llm(ModelCapabilities.for_task("planning"))
        
        prompt = f"Research request: {task.objective}\n\nContext: {task.context}"
        
        try:
            response = await llm.complete(LLMRequest(
                messages=[
                    LLMMessage(role="system", content=self.SYSTEM_PROMPT),
                    LLMMessage(role="user", content=prompt),
                ],
                temperature=0.3,
                json_mode=True,
            ))
            
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