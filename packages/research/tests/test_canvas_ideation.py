import pytest
from research.canvas.ideation import CanvasIdeationEngine


def test_generate_canvas_from_research_defaults():
    result = CanvasIdeationEngine.generate_canvas_from_research(
        title="Sparse Transformer Attention",
        objective="Analyze sub-quadratic computational complexity in large context windows.",
    )
    assert result["title"] == "Canvas: Sparse Transformer Attention"
    assert len(result["nodes"]) >= 4
    assert len(result["edges"]) >= 3
    assert result["background_grid"] == "dots"

    node_types = [n["node_type"] for n in result["nodes"]]
    assert "hypothesis" in node_types
    assert "agent_thought" in node_types
    assert "evidence" in node_types
    assert "conclusion" in node_types


def test_generate_canvas_from_research_custom_findings():
    custom_findings = [
        {"topic": "Linear Memory Scaling", "summary": "Peak VRAM dropped 45% using block-sparse kernels."},
        {"topic": "Accuracy Preservation", "summary": "Perplexity remained within 0.02 of dense attention."},
    ]
    custom_evidence = [
        {"claim": "Empirical benchmark on 8x H100 GPUs", "source": "MLSys 2026 Proceedings"},
    ]
    conclusions = ["Sparse kernels are viable for production 1M token contexts."]

    result = CanvasIdeationEngine.generate_canvas_from_research(
        title="Sparse Attention Kernels",
        objective="Validate memory and compute scaling.",
        findings=custom_findings,
        evidence=custom_evidence,
        conclusions=conclusions,
    )

    assert len(result["nodes"]) == 5  # 1 root + 2 findings + 1 evidence + 1 conclusion
    assert len(result["edges"]) >= 4


def test_synthesize_agent_brainstorm_nodes():
    existing_nodes = [
        {"id": "n1", "position_x": 100.0, "position_y": 100.0},
        {"id": "n2", "position_x": 400.0, "position_y": 200.0},
    ]
    brainstorm = CanvasIdeationEngine.synthesize_agent_brainstorm_nodes(
        topic="Sparse Transformer Attention",
        existing_nodes=existing_nodes,
    )

    assert "brainstormed_nodes" in brainstorm
    assert len(brainstorm["brainstormed_nodes"]) == 2
    assert "brainstormed_edges" in brainstorm
    assert len(brainstorm["brainstormed_edges"]) == 2

    types = [n["node_type"] for n in brainstorm["brainstormed_nodes"]]
    assert "counter_claim" in types
    assert "hypothesis" in types


def test_detect_canvas_clusters():
    nodes = [
        {"id": "a"},
        {"id": "b"},
        {"id": "c"},
        {"id": "d"},
    ]
    # Cluster 1: a - b; Cluster 2: c - d
    edges = [
        {"source_node_id": "a", "target_node_id": "b"},
        {"source_node_id": "c", "target_node_id": "d"},
    ]

    clusters = CanvasIdeationEngine.detect_canvas_clusters(nodes, edges)
    assert len(clusters) == 2
    assert {c["node_count"] for c in clusters} == {2}
