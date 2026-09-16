"""
Tests for Phase 56: Epigenomics Engine.
"""
from research.epigenomics.epigenomics_engine import EpigenomicsEngine


def test_call_peaks_and_motifs():
    peaks = EpigenomicsEngine.call_peaks_and_motifs(
        sample_id="TEST-SAM",
        target_genes=["PDCD1", "CTLA4", "HAVCR2"],
        depth_m=50.0,
    )
    assert len(peaks) == 3
    for p in peaks:
        assert "chromosome" in p
        assert p["start_pos"] < p["end_pos"]
        assert len(p["motifs"]) >= 1
