"""Tests for SpatialRNAVelocityEngine."""

from research.spatial.spatial_rna_velocity_engine import (
    SpatialRNAVelocityEngine,
    SpatialVelocitySimulationRequest,
)


def test_spatial_rna_velocity_engine():
    engine = SpatialRNAVelocityEngine()
    req = SpatialVelocitySimulationRequest(
        tissue_sample="Embryonic Spinal Cord",
        developmental_stage="E12.5",
        spot_count=800,
        splicing_rate_gamma=1.2,
    )
    res = engine.simulate(req)
    assert res.status == "COMPLETED"
    assert res.mean_speed > 0
    assert len(res.spots) == 5
    assert len(res.streamlines) == 2
