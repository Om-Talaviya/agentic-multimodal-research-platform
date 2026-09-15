"""Tests for PaperAnalysisTool and MethodologyComparisonTool in packages/tools."""

import pytest
from tools.definitions.paper_analysis import PaperAnalysisTool, MethodologyComparisonTool


@pytest.fixture
def paper_tool() -> PaperAnalysisTool:
    return PaperAnalysisTool()


@pytest.fixture
def comparison_tool() -> MethodologyComparisonTool:
    return MethodologyComparisonTool()


@pytest.mark.asyncio
async def test_paper_analysis_extract_structure(paper_tool: PaperAnalysisTool):
    sample_struct = {
        "title": "DeepSeek-R1: Incentivizing Reasoning Capability via RL",
        "authors": ["DeepSeek-AI", "Daya Guo", "Dejian Yang"],
        "abstract": "We introduce DeepSeek-R1, which incorporates multi-stage training and cold-start data.",
        "sections": [
            {"title": "1. Introduction", "section_type": "introduction", "content": "Introductory content."},
            {"title": "2. Methods", "section_type": "methodology", "content": "Reinforcement learning details."},
            {"title": "3. Limitations", "section_type": "limitations", "content": "Language mixing limitations."},
        ],
        "methodology_summary": "Reinforcement learning details.",
        "limitations_summary": "Language mixing limitations.",
        "bibliography": [{"id": "1", "citation_key": "[1]"}],
    }

    res = await paper_tool.execute(operation="extract_structure", paper_structure=sample_struct)
    assert res.success is True
    assert res.data["title"] == "DeepSeek-R1: Incentivizing Reasoning Capability via RL"
    assert res.data["section_count"] == 3
    assert res.data["has_limitations"] is True
    assert res.data["reference_count"] == 1


@pytest.mark.asyncio
async def test_paper_analysis_query_section(paper_tool: PaperAnalysisTool):
    sample_struct = {
        "sections": [
            {"title": "1. Introduction", "section_type": "introduction", "content": "Intro text."},
            {"title": "2. Methodology", "section_type": "methodology", "content": "Architecture formulation."},
        ]
    }

    res = await paper_tool.execute(
        operation="query_section",
        paper_structure=sample_struct,
        section_type="methodology",
    )
    assert res.success is True
    assert res.data["matches_found"] == 1
    assert res.data["sections"][0]["title"] == "2. Methodology"


@pytest.mark.asyncio
async def test_methodology_comparison(comparison_tool: MethodologyComparisonTool):
    papers = [
        {
            "title": "Transformer (2017)",
            "methodology": "Self-attention mechanism without recurrence",
            "benchmarks": ["WMT 2014 En-De", "WMT 2014 En-Fr"],
            "results": {"BLEU_EnDe": 28.4, "BLEU_EnFr": 41.8},
            "limitations": "Quadratic memory scaling O(N^2) with sequence length",
        },
        {
            "title": "Mamba (2023)",
            "methodology": "Selective state space models (SSM) with linear time invariance",
            "benchmarks": ["The Pile", "WikiText-103"],
            "results": {"Perplexity": 8.7, "Inference_Speedup": "5x"},
            "limitations": "Reduced expressivity on strict associative recall tasks",
        },
    ]

    res = await comparison_tool.execute(papers=papers, comparison_focus="all")
    assert res.success is True
    assert res.data["paper_count"] == 2
    assert "Cross-Paper Methodology" in res.data["comparison_matrix_markdown"]
    assert "Transformer (2017)" in res.data["comparison_matrix_markdown"]
    assert "Mamba (2023)" in res.data["comparison_matrix_markdown"]
    assert "Self-attention" in res.data["comparison_matrix_markdown"]
