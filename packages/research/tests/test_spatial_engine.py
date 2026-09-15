"""Unit tests for Spatial Transcriptomics Engine (Phase 42)."""
import pytest
from research.spatial_engine import SpatialTranscriptomicsEngine

def test_spatial_engine_tissue_analysis():
    engine = SpatialTranscriptomicsEngine(seed=123)
    res = engine.analyze_tissue_sample(
        tissue_type="Glioblastoma Multiforme",
        n_spots=150,
        technology="10x Visium",
    )

    assert "spots" in res
    assert "domains" in res
    assert "communications" in res
    assert "summary" in res

    spots = res["spots"]
    assert len(spots) == 150
    assert "spot_barcode" in spots[0]
    assert "x_coord" in spots[0]
    assert "tumor_proximity_score" in spots[0]
    assert 0.0 <= spots[0]["tumor_proximity_score"] <= 1.0

    domains = res["domains"]
    assert len(domains) == 4
    domain_names = [d["domain_name"] for d in domains]
    assert "Tumor Core" in domain_names
    assert "Cancer-Associated Stroma" in domain_names

    comms = res["communications"]
    assert len(comms) >= 4
    pathways = [c["pathway_name"] for c in comms]
    assert "VEGF" in pathways
    assert "TGFb" in pathways
