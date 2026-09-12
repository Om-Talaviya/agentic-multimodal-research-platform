"""Document analysis agent - processes uploaded documents and multimodal ingestion outputs."""

import json
import uuid
from typing import Any, Dict, List
from agents.base import Agent, AgentContext, AgentResult
from research.models import ResearchTask, Source, Evidence, Citation, CitationCoordinates
from ai.schemas import LLMRequest, LLMMessage, ModelCapabilities
from ai.providers.router import ModelRouter
from tools.registry import tool_registry
from shared.logging import get_logger

logger = get_logger(__name__)


class DocumentAnalysisAgent(Agent):
    """Analyzes uploaded documents, structured chunks, tabular datasets, and visual annotations."""

    name = "document_analysis"
    description = "Analyzes documents, datasets, tables, and multimodal ingestion chunks to extract grounded evidence"
    capabilities = {
        "document_analysis",
        "content_extraction",
        "table_analysis",
        "multimodal_reasoning",
        "data_analysis",
        "statistical_computation",
    }

    SYSTEM_PROMPT = """You are an expert multimodal document and dataset analysis agent.
Your task is to analyze document contents, structured tables, dataset statistics, and visual diagram annotations to extract grounded factual findings relevant to the research objective.

When analyzing:
- Extract clear, unambiguous claims supported by the document text, tables, dataset profiles, or image annotations.
- For quantitative data and tabular datasets, extract exact figures, computed means/medians, trends, and comparative metrics.
- Cite the source chunk index, page number, paragraph index, table coordinates, or dataset column where each piece of evidence originates.

Return findings as a valid JSON object:
{
    "findings": [
        {
            "claim": "Specific factual claim or finding",
            "evidence": "Exact excerpt, computed statistic, table cell/row, or diagram annotation supporting the claim",
            "confidence": 0.9,
            "section": "Optional section name or chunk identifier",
            "modality": "text|table|image|dataset",
            "page_number": 1,
            "paragraph_index": 2,
            "table_row": null,
            "table_col": null,
            "exact_quote": "Exact supporting quote from the document text"
        }
    ],
    "summary": "Brief synthesis of document insights"
}
"""

    async def run(self, task: ResearchTask, context: AgentContext) -> AgentResult:
        doc_read_tool = context.tools.get("document_read") or tool_registry.get("document_read")
        knowledge_search_tool = context.tools.get("knowledge_search") or tool_registry.get("knowledge_search")
        data_analysis_tool = context.tools.get("data_analysis") or tool_registry.get("data_analysis")
        math_tool = context.tools.get("deterministic_math") or tool_registry.get("deterministic_math")

        document_ids = task.inputs.get("document_ids", [])
        if not document_ids and "document_id" in task.inputs:
            document_ids = [task.inputs["document_id"]]

        evidence_list: List[Evidence] = []
        sources_list: List[Source] = []

        try:
            # 1. Direct document reading flow
            if document_ids and doc_read_tool:
                for doc_id in document_ids:
                    doc_str = str(doc_id)
                    content = await doc_read_tool.execute(document_id=doc_str)

                    if not content or len(content.strip()) < 10:
                        logger.warning("Empty or unreadable document content", doc_id=doc_str)
                        continue

                    extract_response = await context.complete_llm(
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
                        ),
                        task="research",
                    )

                    raw_content = extract_response.content.strip()
                    if raw_content.startswith("```"):
                        lines = raw_content.splitlines()
                        if lines[0].startswith("```"):
                            lines = lines[1:]
                        if lines and lines[-1].startswith("```"):
                            lines = lines[:-1]
                        raw_content = "\n".join(lines).strip()

                    parsed_result = json.loads(raw_content)
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
                        coords = None
                        if any(item.get(k) is not None for k in ("page_number", "paragraph_index", "table_row", "table_col")):
                            coords = CitationCoordinates(
                                page_number=item.get("page_number"),
                                paragraph_index=item.get("paragraph_index"),
                                table_row=item.get("table_row"),
                                table_col=item.get("table_col"),
                            )

                        citation = Citation(
                            id=str(uuid.uuid4()),
                            claim=item.get("claim", ""),
                            source_id=source.id,
                            document_id=doc_str,
                            citation_text=item.get("section") or f"Page {item.get('page_number', 1)}",
                            quote=item.get("exact_quote") or item.get("evidence", ""),
                            coordinates=coords,
                            confidence=float(item.get("confidence", 0.85)),
                        )

                        ev = Evidence(
                            id=str(uuid.uuid4()),
                            source_id=source.id,
                            claim=item.get("claim", ""),
                            supporting_text=item.get("evidence", ""),
                            confidence=float(item.get("confidence", 0.8)),
                            coordinates=coords,
                            citations=[citation],
                        )
                        evidence_list.append(ev)

                    context.memory.set_long_term(f"doc_{doc_str}_findings", [f.get("claim") for f in findings])

            # 2. Hybrid knowledge search flow (when no explicit doc IDs or search query given)
            query = task.inputs.get("query") or (task.objective if not document_ids else None)
            if query and knowledge_search_tool:
                search_results = await knowledge_search_tool.execute(query=query, top_k=5)
                if search_results:
                    combined_chunks_text = []
                    for idx, res in enumerate(search_results):
                        chunk_text = res.get("content", "")
                        citation = res.get("citation", f"Chunk {idx}")
                        combined_chunks_text.append(f"[{citation}]\n{chunk_text}")

                    rag_context_text = "\n\n---\n\n".join(combined_chunks_text)
                    rag_response = await context.complete_llm(
                        LLMRequest(
                            messages=[
                                LLMMessage(role="system", content=self.SYSTEM_PROMPT),
                                LLMMessage(
                                    role="user",
                                    content=f"Research Objective: {task.objective}\n\nRetrieved Knowledge Base Chunks:\n{rag_context_text[:25000]}",
                                ),
                            ],
                            temperature=0.2,
                            json_mode=True,
                        ),
                        task="research",
                    )

                    rag_raw = rag_response.content.strip()
                    if rag_raw.startswith("```"):
                        lines = rag_raw.splitlines()
                        if lines[0].startswith("```"):
                            lines = lines[1:]
                        if lines and lines[-1].startswith("```"):
                            lines = lines[:-1]
                        rag_raw = "\n".join(lines).strip()

                    rag_parsed = json.loads(rag_raw)
                    rag_findings = rag_parsed.get("findings", [])

                    rag_source = Source(
                        id=str(uuid.uuid4()),
                        type="knowledge_base",
                        title=f"Knowledge Base: {query[:40]}",
                        metadata={
                            "query": query,
                            "chunk_count": len(search_results),
                            "summary": rag_parsed.get("summary", ""),
                        },
                    )
                    sources_list.append(rag_source)

                    for item in rag_findings:
                        coords = None
                        if any(item.get(k) is not None for k in ("page_number", "paragraph_index", "table_row", "table_col")):
                            coords = CitationCoordinates(
                                page_number=item.get("page_number"),
                                paragraph_index=item.get("paragraph_index"),
                                table_row=item.get("table_row"),
                                table_col=item.get("table_col"),
                            )

                        citation = Citation(
                            id=str(uuid.uuid4()),
                            claim=item.get("claim", ""),
                            source_id=rag_source.id,
                            citation_text=item.get("section") or "Knowledge Base",
                            quote=item.get("exact_quote") or item.get("evidence", ""),
                            coordinates=coords,
                            confidence=float(item.get("confidence", 0.85)),
                        )

                        ev = Evidence(
                            id=str(uuid.uuid4()),
                            source_id=rag_source.id,
                            claim=item.get("claim", ""),
                            supporting_text=item.get("evidence", ""),
                            confidence=float(item.get("confidence", 0.85)),
                            coordinates=coords,
                            citations=[citation],
                        )
                        evidence_list.append(ev)

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