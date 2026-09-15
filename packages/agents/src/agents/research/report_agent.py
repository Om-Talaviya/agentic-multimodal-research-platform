"""Report generation agent - synthesizes verified evidence into a structured research report."""

import json
from typing import Any, Dict, List, Optional
from uuid import uuid4
from agents.base import Agent, AgentContext, AgentResult
from research.models import ResearchTask, Evidence, Source, Finding, Citation, CitationCoordinates, Contradiction
from ai.schemas import LLMMessage, LLMRequest, ModelCapabilities
from ai.providers.router import ModelRouter
from shared.logging import get_logger

logger = get_logger(__name__)


class ReportAgent(Agent):
    """Synthesizes verified research evidence into a structured report."""

    name = "report"
    description = "Synthesizes verified evidence into a comprehensive research report"
    capabilities = {"synthesis", "report_generation", "summarization"}

    SYSTEM_PROMPT = """You are a rigorous research synthesis agent. Your task is to generate a comprehensive, well-structured, citation-grounded research report from verified evidence and critic evaluations.

GUIDELINES:
1. Base ALL claims and findings strictly on the provided verified evidence.
2. Link every finding to specific citations and evidence IDs.
3. If contradictions or discrepancies exist between sources, explicitly document them in the contradictions section.
4. Compute an overall quantitative factual confidence score (0.0 to 1.0) reflecting evidence grounding and consensus.
5. Organize findings into logical themes/sections.
6. Generate an executive summary that captures key conclusions and nuance.
7. Describe the methodology used to gather and verify evidence.
8. List limitations honestly (evidence gaps, potential biases, unverified claims).

OUTPUT FORMAT (JSON):
{
    "title": "Report title",
    "executive_summary": "Concise summary of key findings and conclusions",
    "methodology": "Description of research methodology, sources, and verification process",
    "findings": [
        {
            "topic": "Theme or topic name",
            "summary": "Detailed finding summary with evidence citations [evidence_id]",
            "evidence_ids": ["evidence_id1", "evidence_id2"],
            "citations": [
                {
                    "claim": "Specific factual claim",
                    "source_id": "source_id",
                    "citation_text": "Section or page reference",
                    "quote": "Exact supporting quote",
                    "confidence": 0.95
                }
            ],
            "confidence": 0.85,
            "uncertainty": "Any caveats or uncertainty about this finding",
            "assumptions": ["Any assumptions made"]
        }
    ],
    "contradictions": [
        {
            "topic": "Conflict topic",
            "claim_a": "Statement from first source",
            "source_a": "Source A",
            "claim_b": "Conflicting statement from second source",
            "source_b": "Source B",
            "conflict_type": "direct_conflict|numerical_discrepancy|methodological_divergence",
            "explanation": "Explanation of discrepancy",
            "severity": "low|medium|high"
        }
    ],
    "confidence_score": 0.88,
    "conclusions": ["Conclusion 1 supported by evidence", "Conclusion 2"],
    "limitations": ["Limitation 1", "Limitation 2", "Gap in evidence for X"]
}"""

    async def run(self, task: ResearchTask, context: AgentContext) -> AgentResult:
        """Generate report from verified evidence."""
        # Get verified evidence and contradictions from task inputs or memory
        evidence_items = task.inputs.get("evidence", [])
        sources = task.inputs.get("sources", [])
        input_contradictions = task.inputs.get("contradictions") or context.memory.get_working("last_contradictions") or []
        input_confidence = task.inputs.get("confidence_score") or context.memory.get_working("last_confidence_score")
        question = task.inputs.get("question") or task.objective

        if not evidence_items:
            logger.info("No evidence provided to ReportAgent, generating minimal report", task_id=task.id)
            return self._generate_empty_report(question)

        # Filter for verified evidence (only verified, consensus, single_source)
        verified_evidence = []
        for ev in evidence_items:
            if isinstance(ev, dict):
                verification_status = ev.get("verification_status", "unverified")
                if verification_status in ("verified", "consensus", "single_source"):
                    verified_evidence.append(ev)
            elif hasattr(ev, "verification_status"):
                if getattr(ev, "verification_status", "unverified") in ("verified", "consensus", "single_source"):
                    verified_evidence.append(ev)

        if not verified_evidence:
            logger.info("No verified evidence found, generating empty report", task_id=task.id)
            return self._generate_empty_report(question)

        # Format evidence for LLM
        formatted_evidence = []
        for i, ev in enumerate(verified_evidence):
            if isinstance(ev, dict):
                ev_id = ev.get("id", f"ev_{i}")
                claim = ev.get("claim", "")
                text = ev.get("supporting_text", "")
                confidence = ev.get("confidence", 0.5)
                status = ev.get("verification_status", "unverified")
                src_id = ev.get("source_id", "")
                coords = ev.get("citation_coordinates") or ev.get("coordinates") or {}
            elif hasattr(ev, "claim"):
                ev_id = str(getattr(ev, "id", f"ev_{i}"))
                claim = getattr(ev, "claim", "")
                text = getattr(ev, "supporting_text", "")
                confidence = getattr(ev, "confidence", 0.5)
                status = getattr(ev, "verification_status", "unverified")
                src_id = str(getattr(ev, "source_id", ""))
                coords = getattr(ev, "coordinates", None) or getattr(ev, "citation_coordinates", None) or {}
            else:
                continue

            coord_str = f" | Coordinates: {coords}" if coords else ""
            formatted_evidence.append(
                f"[Evidence ID: {ev_id} | Source ID: {src_id} | Status: {status} | Confidence: {confidence:.2f}{coord_str}]\n"
                f"Claim: {claim}\n"
                f"Supporting Text: {text[:3000]}\n"
            )

        # Format sources
        formatted_sources = []
        for src in sources:
            if isinstance(src, dict):
                src_id = src.get("id", "")
                src_title = src.get("title", "")
                src_url = src.get("url", "")
                src_type = src.get("type", "")
            elif hasattr(src, "title"):
                src_id = str(getattr(src, "id", ""))
                src_title = getattr(src, "title", "")
                src_url = getattr(src, "url", "")
                src_type = getattr(src, "type", "")
            else:
                continue
            formatted_sources.append(f"[Source {src_id}] {src_title} ({src_type}) - {src_url}")

        contradictions_prompt = ""
        if input_contradictions:
            contradictions_prompt = f"\n\nPre-Identified Contradictions ({len(input_contradictions)} items):\n" + json.dumps(input_contradictions, indent=2)

        user_content = (
            f"Research Question: {question}\n\n"
            f"Verified Evidence ({len(formatted_evidence)} items):\n\n"
            + "\n---\n".join(formatted_evidence[:30])
            + f"\n\nSources ({len(formatted_sources)}):\n"
            + "\n".join(formatted_sources[:20])
            + contradictions_prompt
            + "\n\nGenerate a comprehensive research report in the specified JSON format."
        )

        try:
            response = await context.complete_llm(
                LLMRequest(
                    messages=[
                        LLMMessage(role="system", content=self.SYSTEM_PROMPT),
                        LLMMessage(role="user", content=user_content),
                    ],
                    temperature=0.2,
                    json_mode=True,
                ),
                task="report",
            )

            raw_content = response.content.strip()
            if raw_content.startswith("```"):
                lines = raw_content.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                raw_content = "\n".join(lines).strip()

            result_data = json.loads(raw_content)

            # Create Finding objects from the report
            findings = []
            for f in result_data.get("findings", []):
                raw_citations = f.get("citations", [])
                citations_list = []
                for c in raw_citations:
                    citations_list.append(
                        Citation(
                            id=str(uuid4()),
                            claim=c.get("claim", ""),
                            source_id=c.get("source_id"),
                            document_id=c.get("document_id"),
                            citation_text=c.get("citation_text", ""),
                            quote=c.get("quote", ""),
                            confidence=float(c.get("confidence", 0.85)),
                        )
                    )

                finding = Finding(
                    id=str(uuid4()),
                    topic=f.get("topic", ""),
                    summary=f.get("summary", ""),
                    evidence_ids=f.get("evidence_ids", []),
                    citations=citations_list,
                    confidence=float(f.get("confidence", 0.7)),
                    uncertainty=f.get("uncertainty"),
                    assumptions=f.get("assumptions", []),
                )
                findings.append(finding)

            # Process contradictions
            raw_contradictions = result_data.get("contradictions") or input_contradictions or []
            contradictions_list = []
            for item in raw_contradictions:
                if isinstance(item, dict):
                    contradictions_list.append(
                        Contradiction(
                            id=str(uuid4()),
                            topic=item.get("topic", "General"),
                            claim_a=item.get("claim_a", ""),
                            source_a=item.get("source_a", ""),
                            claim_b=item.get("claim_b", ""),
                            source_b=item.get("source_b", ""),
                            conflict_type=item.get("conflict_type", "direct_conflict"),
                            explanation=item.get("explanation", ""),
                            severity=item.get("severity", "medium"),
                        )
                    )

            # Determine confidence score
            confidence_score = float(result_data.get("confidence_score") or input_confidence or 0.85)

            # Build report output
            report_output = {
                "title": result_data.get("title", f"Research Report: {question}"),
                "executive_summary": result_data.get("executive_summary", ""),
                "methodology": result_data.get("methodology", ""),
                "findings": [f.model_dump() for f in findings],
                "evidence_ids": [str(ev.get("id", "")) if isinstance(ev, dict) else str(getattr(ev, "id", "")) for ev in verified_evidence],
                "source_ids": [str(src.get("id", "")) if isinstance(src, dict) else str(getattr(src, "id", "")) for src in sources],
                "contradictions": [c.model_dump() for c in contradictions_list],
                "confidence_score": confidence_score,
                "conclusions": result_data.get("conclusions", []),
                "limitations": result_data.get("limitations", []),
            }

            logger.info(
                "ReportAgent generated report",
                task_id=task.id,
                findings_count=len(findings),
                contradictions_count=len(contradictions_list),
                confidence_score=confidence_score,
                evidence_count=len(verified_evidence),
            )

            return AgentResult(
                success=True,
                output=report_output,
                metadata={
                    "model": response.model,
                    "findings_count": len(findings),
                    "contradictions_count": len(contradictions_list),
                    "confidence_score": confidence_score,
                    "evidence_count": len(verified_evidence),
                },
            )

        except Exception as e:
            logger.error("ReportAgent generation failed", error=str(e), task_id=task.id)
            return AgentResult(
                success=False,
                errors=[f"Report generation failed: {str(e)}"],
            )

    def _generate_empty_report(self, question: str) -> AgentResult:
        """Generate a minimal report when no evidence is available."""
        from datetime import UTC, datetime
        from research.models import ResearchReport

        report = ResearchReport(
            id=str(uuid4()),
            job_id="",
            title=f"Research Report: {question}",
            executive_summary="No evidence was gathered for this research question.",
            methodology="No research was conducted due to lack of available evidence.",
            findings=[],
            evidence=[],
            sources=[],
            contradictions=[],
            confidence_score=0.0,
            conclusions=[],
            limitations=["No evidence available to support any findings."],
            generated_at=datetime.now(UTC),
        )

        return AgentResult(
            success=True,
            output=report.model_dump(),
            metadata={"empty_report": True},
        )
