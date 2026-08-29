"""Web research agent - searches and extracts information from the web."""

import uuid
from agents.base import Agent, AgentContext, AgentResult
from research.models import ResearchTask, Source, Evidence
from ai.schemas import LLMRequest, LLMMessage
from ai.providers.router import ModelRouter
from ai.schemas import ModelCapabilities
from tools.registry import tool_registry
from shared.logging import get_logger

logger = get_logger(__name__)


class WebResearchAgent(Agent):
    """Searches and extracts information from the web."""
    
    name = "web_research"
    description = "Searches the web and extracts relevant information"
    capabilities = {"web_search", "content_extraction", "fact_finding"}
    
    SYSTEM_PROMPT = """You are a web research agent. Your task is to find relevant information
    for the given research question. Use the web_search tool to find sources, then web_fetch
    to retrieve content. Extract key facts, citations, and evidence.
    
    Always cite your sources with URLs. Be specific and factual.
    Return JSON array of findings: [{"claim": "...", "evidence": "...", "confidence": 0.8}]
    """
    
    async def run(self, task: ResearchTask, context: AgentContext) -> AgentResult:
        router: ModelRouter = context.model_router
        llm = router.select_llm(ModelCapabilities.for_task("research"))
        
        search_tool = tool_registry.get("web_search")
        fetch_tool = tool_registry.get("web_fetch")
        
        if not search_tool or not fetch_tool:
            return AgentResult(
                success=False,
                errors=["Required tools not available: web_search, web_fetch"],
            )
        
        try:
            # Search
            query = task.inputs.get("query", task.objective)
            search_results = await search_tool.execute(query=query, max_results=10)
            
            if not search_results:
                return AgentResult(
                    success=True,
                    output={"sources": [], "evidence": []},
                    metadata={"sources_found": 0},
                )
            
            evidence = []
            sources = []
            
            for result in search_results[:5]:  # Limit for MVP
                try:
                    content = await fetch_tool.execute(url=result.get("url", ""))
                    
                    if not content or len(content) < 100:
                        continue
                    
                    # Extract evidence using LLM
                    extract_response = await llm.complete(LLMRequest(
                        messages=[
                            LLMMessage(role="system", content="Extract key facts from this content relevant to the research question. Return JSON array of {claim, evidence, confidence}."),
                            LLMMessage(role="user", content=f"Question: {task.objective}\n\nContent: {content[:10000]}"),
                        ],
                        temperature=0.2,
                        json_mode=True,
                    ))
                    
                    import json
                    facts = json.loads(extract_response.content)
                    
                    source = Source(
                        id=str(uuid.uuid4()),
                        type="web",
                        url=result.get("url"),
                        title=result.get("title", "Untitled"),
                        metadata={"snippet": result.get("snippet"), "domain": result.get("domain")},
                    )
                    sources.append(source)
                    
                    for fact in facts:
                        evidence.append(Evidence(
                            id=str(uuid.uuid4()),
                            source_id=source.id,
                            claim=fact.get("claim", ""),
                            supporting_text=fact.get("evidence", ""),
                            confidence=fact.get("confidence", 0.7),
                        ))
                        
                except Exception as e:
                    logger.warning("Failed to process search result", url=result.get("url"), error=str(e))
                    continue
            
            logger.info("Web research completed", job_id=context.research_job_id, sources=len(sources), evidence=len(evidence))
            
            return AgentResult(
                success=True,
                output={"sources": sources, "evidence": evidence},
                evidence=evidence,
                metadata={"sources_found": len(sources), "evidence_count": len(evidence)},
            )
            
        except Exception as e:
            logger.error("Web research failed", error=str(e))
            return AgentResult(
                success=False,
                errors=[f"Web research failed: {e}"],
            )