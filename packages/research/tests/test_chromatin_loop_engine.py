"""Tests for ChromatinLoopEngine (Phase 152)."""

from research.genomics.chromatin_loop_engine import (
    ChromatinLoopEngine,
    ChromatinLoopRequest,
)


def test_chromatin_loop_engine():
    engine = ChromatinLoopEngine()
    req = ChromatinLoopRequest(
        cell_line_name="HepG2",
        chromosome="chr8",
        genomic_window_start_bp=127000000,
        genomic_window_end_bp=129000000,
        resolution_bp=5000,
    )
    result = engine.map_loops(req)
    assert result.total_loops_detected >= 3
    assert result.tad_count >= 3
    assert result.mean_loop_span_kb > 0
    assert len(result.contact_edges) >= 3
    assert len(result.tad_boundaries) >= 3
