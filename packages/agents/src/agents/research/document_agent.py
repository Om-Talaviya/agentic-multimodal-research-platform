"""Document analysis agent - processes uploaded documents."""

import uuid
from agents.base import Agent, AgentContext, AgentResult
from research.models import ResearchTask, Source, Evidence
from ai.schemas import LLMRequest, LLMMessage
from ai.providers.router import ModelRouter
from ai.schemas import ModelCapabilities
from tools.registry import tool_registry
from shared.logging import get_logger

logger = get_logger(__name__)


class DocumentAnalysisAgent(Agent):
    """Analyzes uploaded documents for relevant information."""
    
    name = "document_analysis"
    description = "Analyzes uploaded documents and extracts relevant information"
    capabilities = {"document_analysis", "content_extraction", "fact_finding"}
    
    SYSTEM_PROMPT = """You are a document analysis agent. Extract key facts from the provided
    document content relevant to the research question.
    Return JSON array of findings: [{"claim": "...", "evidence": "...", "confidence": 0.8}]
    """
    
    async def run(self, task: ResearchTask, context: AgentContext) -> AgentResult:
        router: ModelRouter = context.model_router
        llm = router.select_llm(ModelCapabilities.for_task("research"))
        
        doc_read_tool = tool_registry.get("document_read")
        
        if not doc_read_tool:
            return AgentResult(
                success=False,
                errors=["Required tool not available: document_read"],
            )
        
        document_ids = task.inputs.get("document_ids", [])
        if not document_ids:
            return AgentResult(
                success=True,
                output={"sources": [], "evidence": []},
                metadata={"documents_processed": 0},
            )
        
        evidence = []
        sources = []
        
        try:
            for doc_id in document_ids:
                content = await doc_read_tool.execute(document_id=doc_id)
                
                if not content or len(content) < 50:
                    continue
                
                # Extract evidence
                extract_response = await llm.complete(LLMRequest(
                    messages=[
                        LLMMessage(role="system", content=self.SYSTEM_PROMPT),
                        LLMMessage(role="user", content=f"Question: {task.objective}\n\nDocument: {content[:15000]}"),
                    ],
                    temperature=0.2,
                    json_mode=True,
                ))
                
                import json
                facts = json.loads(extract_response.content)
                
                source = Source(
                    id=str(uuid.uuid4()),
                    type="document",
                    title=f"Document {doc_id[:8]}",
                    metadata={"document_id": doc_id},
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
            
            logger.info("Document analysis completed", job_id=context.research_job_id, docs=len(sources), evidence=len(evidence))
            
            return AgentResult(
                success=True,
                output={"sources": sources, "evidence": evidence},
                evidence=evidence,
                metadata={"documents_processed": len(sources), "evidence_count": len(evidence)},
            )
            
        except Exception as e:
            logger.error("Document analysis failed", error=str(e))
            return AgentResult(
                success=False,
                errors=[f"Document analysis failed: {e}"],
            )