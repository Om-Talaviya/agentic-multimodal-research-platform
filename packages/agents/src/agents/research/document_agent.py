"""Document analysis agent - processes uploaded documents and multimodal ingestion outputs."""

import json
import uuid
from typing import Any, Dict, List
from agents.base import Agent, AgentContext, AgentResult
from research.models import ResearchTask, Source, Evidence
from ai.schemas import LLMRequest, LLMMessage, ModelCapabilities
from ai.providers.router import ModelRouter
from tools.registry import tool_registry
from shared.logging import get_logger

logger = get_logger(__name__)


class DocumentAnalysisAgent(Agent):
    """Analyzes uploaded documents, structured chunks, tables, and visual annotations."""

    name = "document_analysis"
    description = "Analyzes documents, tables, and multimodal ingestion chunks to extract grounded evidence"
    capabilities = {"document_analysis", "content_extraction", "table_analysis", "multimodal_reasoning"}

    SYSTEM_PROMPT = """You are an expert multimodal document analysis agent.
Your task is to analyze document contents, structured tables, and visual diagram annotations to extract grounded factual findings relevant to the research objective.

When analyzing:
- Extract clear, unambiguous claims supported by the document text, tables, or image annotations.
- For quantitative data in tables, extract exact figures, trends, and comparative metrics.
- Cite the source chunk index or section where each piece of evidence originates.

Return findings as a valid JSON object:
{
    "findings": [
        {
            "claim": "Specific factual claim or finding",
            "evidence": "Exact excerpt, table cell/row, or diagram annotation supporting the claim",
            "confidence": 0.9,
            "section": "Optional section name or chunk identifier",
            "modality": "text|table|image"
        }
    ],
    "summary": "Brief synthesis of document insights"
}
"""

    async def run(self, task: ResearchTask, context: AgentContext) -> AgentResult:
        router: ModelRouter = context.model_router
        llm = router.select_llm(ModelCapabilities.for_task("research"))

        doc_read_tool = context.tools.get("document_read") or tool_registry.get("document_read")
        if not doc_read_tool:
            return AgentResult(
                success=False,
                errors=["Required tool not available: document_read"],
            )

        document_ids = task.inputs.get("document_ids", [])
        if not document_ids and "document_id" in task.inputs:
            document_ids = [task.inputs["document_id"]]

        if not document_ids:
            return AgentResult(
                success=True,
                output={"sources": [], "evidence": [], "summary": "No documents provided"},
                metadata={"documents_processed": 0},
            )

        evidence_list: List[Evidence] = []
        sources_list: List[Source] = []

        try:
            for doc_id in document_ids:
                doc_str = str(doc_id)
                content = await doc_read_tool.execute(document_id=doc_str)

                if not content or len(content.strip()) < 10:
                    logger.warning("Empty or unreadable document content", doc_id=doc_str)
                    continue

                extract_response = await llm.complete(
                    LLMRequest(
                        messages=[
                            LLMMessage(role="system", content=self.SYSTEM_PROMPT),
                            LLMMessage(
                                role="user",
                                content=f"Research Objective: {task.objective}\n\nDocument Content & Ingestion Data:\n{content[:25000]}",
                            ),
                        ],
                        temperature=0.2,
                        json_mode=True,
                    )
                )

                parsed_result = json.loads(extract_response.content)
                findings = parsed_result.get("findings", [])

                source = Source(
                    id=str(uuid.uuid4()),
                    type="document",
                    title=f"Document {doc_str[:8]}",
                    metadata={
                        "document_id": doc_str,
                        "summary": parsed_result.get("summary", ""),
                    },
                )
                sources_list.append(source)

                for item in findings:
                    ev = Evidence(
                        id=str(uuid.uuid4()),
                        source_id=source.id,
                        claim=item.get("claim", ""),
                        supporting_text=item.get("evidence", ""),
                        confidence=float(item.get("confidence", 0.8)),
                    )
                    evidence_list.append(ev)

                # Store document findings in context memory
                context.memory.set_long_term(f"doc_{doc_str}_findings", [f.get("claim") for f in findings])

            logger.info(
                "DocumentAnalysisAgent finished analysis",
                task_id=task.id,
                docs_count=len(sources_list),
                evidence_count=len(evidence_list),
            )

            return AgentResult(
                success=True,
                output={
                    "sources": sources_list,
                    "evidence": evidence_list,
                    "documents_processed": len(sources_list),
                },
                evidence=evidence_list,
                metadata={
                    "documents_processed": len(sources_list),
                    "evidence_count": len(evidence_list),
                },
            )

        except Exception as e:
            logger.error("Document analysis failed", error=str(e), task_id=task.id)
            return AgentResult(
                success=False,
                errors=[f"Document analysis failed: {str(e)}"],
            )