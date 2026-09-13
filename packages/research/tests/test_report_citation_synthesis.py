"""Unit tests for ReportAgent structured citations and contradiction matrix synthesis."""

import json
from unittest.mock import AsyncMock, MagicMock
import pytest
from agents.base import AgentContext
from agents.research.report_agent import ReportAgent
from agents.memory import AgentMemory
from research.models import ResearchTask
from ai.schemas import LLMResponse


@pytest.mark.asyncio
async def test_report_agent_citation_and_contradictions_synthesis():
    """ReportAgent synthesizes findings with nested citations and preserves contradictions."""
    mock_llm = MagicMock()
    mock_llm.complete = AsyncMock(
        return_value=LLMResponse(
            content=json.dumps({
                "title": "Quantum Supremacy Benchmark Report",
                "executive_summary": "Comparative analysis of superconducting versus photonic quantum devices.",
                "methodology": "Cross-verification of 5 benchmark publications.",
                "findings": [
                    {
                        "topic": "Superconducting Qubit Coherence",
                        "summary": "T1 coherence times reached 150 microseconds under cryogenic conditions [ev_1].",
                        "evidence_ids": ["ev_1"],
                        "citations": [
                            {
                                "claim": "T1 coherence times reached 150 microseconds",
                                "source_id": "src_1",
                                "citation_text": "Figure 4, Page 6",
                                "quote": "Average T1 times across 64 transmon qubits was measured at 152 ± 4 us.",
                                "confidence": 0.95
                            }
                        ],
                        "confidence": 0.92,
                        "uncertainty": "Flux noise fluctuations remain a factor",
                        "assumptions": ["Cryostat held below 15mK"]
                    }
                ],
                "contradictions": [
                    {
                        "topic": "Two-Qubit Gate Fidelity",
                        "claim_a": "CZ gate fidelity is 99.8%.",
                        "source_a": "Lab A Technical Whitepaper",
                        "claim_b": "CZ gate fidelity measured at 98.9% under active randomized benchmarking.",
                        "source_b": "Independent Review 2025",
                        "conflict_type": "methodological_divergence",
                        "explanation": "State tomography vs randomized benchmarking methodologies yield different fidelity bounds.",
                        "severity": "medium"
                    }
                ],
                "confidence_score": 0.89,
                "conclusions": ["Superconducting quantum processors demonstrate scalable coherence."],
                "limitations": ["Photonic systems lack uniform multi-qubit gates."]
            }),
            model="gemini-2.5-pro",
            usage={"prompt_tokens": 600, "completion_tokens": 250, "total_tokens": 850},
        )
    )

    mock_router = MagicMock()
    mock_router.select_llm.return_value = mock_llm

    agent = ReportAgent()
    task = ResearchTask(
        id="task_report_synth_1",
        job_id="job_synth_1",
        type="report",
        objective="Analyze quantum computing benchmarks",
        agent="report",
        inputs={
            "evidence": [
                {
                    "id": "ev_1",
                    "claim": "T1 coherence times reached 150 microseconds",
                    "supporting_text": "Average T1 times across 64 transmon qubits was measured at 152 ± 4 us.",
                    "source_id": "src_1",
                    "confidence": 0.95,
                    "verification_status": "verified"
                }
            ],
            "sources": [
                {
                    "id": "src_1",
                    "type": "document",
                    "url": None,
                    "title": "Quantum Coherence Paper"
                }
            ],
            "question": "What is the latest status of quantum coherence and gate fidelity?",
            "contradictions": [
                {
                    "topic": "Two-Qubit Gate Fidelity",
                    "claim_a": "CZ gate fidelity is 99.8%.",
                    "source_a": "Lab A Technical Whitepaper",
                    "claim_b": "CZ gate fidelity measured at 98.9%.",
                    "source_b": "Independent Review 2025",
                    "conflict_type": "methodological_divergence",
                    "explanation": "State tomography vs randomized benchmarking.",
                    "severity": "medium"
                }
            ],
            "confidence_score": 0.89
        }
    )

    context = AgentContext(
        research_job_id="job_synth_1",
        task_id="task_report_synth_1",
        request_id="req_synth_1",
        tools={},
        memory=AgentMemory(),
        model_router=mock_router,
        config={},
    )

    result = await agent.run(task, context)

    assert result.success is True
    assert "findings" in result.output
    assert len(result.output["findings"]) == 1
    finding = result.output["findings"][0]
    assert len(finding["citations"]) == 1
    assert finding["citations"][0]["quote"] == "Average T1 times across 64 transmon qubits was measured at 152 ± 4 us."
    assert "contradictions" in result.output
    assert len(result.output["contradictions"]) == 1
    assert result.output["contradictions"][0]["conflict_type"] == "methodological_divergence"
    assert result.output["confidence_score"] == 0.89
