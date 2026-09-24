"""
Database repository tests for Phase 162: Spatial Microdissection.
"""

import pytest
from database.repositories.spatial_microdissection_repo import SpatialMicrodissectionRepository


@pytest.mark.asyncio
async def test_spatial_microdissection_repo_lifecycle(db_session):
    repo = SpatialMicrodissectionRepository(db_session)

    session = await repo.create_session(
        sample_name="VisiumHD_Test_Sample",
        tissue_type="Triple-Negative Breast Cancer",
        total_spots_analyzed=25,
        subcellular_resolution_nm=50.0,
        mean_cell_type_entropy=1.245,
    )
    assert session.id is not None
    assert session.sample_name == "VisiumHD_Test_Sample"

    spot = await repo.add_spot_deconvolution(
        session_id=session.id,
        spot_index=0,
        spatial_x_coord=10.0,
        spatial_y_coord=20.0,
        dominant_cell_type="CD8+ Cytotoxic T Cell",
        dominant_cell_proportion=0.75,
        cell_type_composition={"CD8+ Cytotoxic T Cell": 0.75, "Malignant Epithelial": 0.25},
        rna_transcripts_count=420,
    )
    assert spot.id is not None
    assert spot.dominant_cell_type == "CD8+ Cytotoxic T Cell"

    niche = await repo.add_niche_boundary(
        session_id=session.id,
        niche_name="Tumor-Infiltrating Niche",
        boundary_polygon=[{"x": 0.0, "y": 0.0}, {"x": 50.0, "y": 50.0}],
        niche_cellularity_score=0.92,
        tumor_immune_interface_distance_um=8.4,
    )
    assert niche.id is not None
    assert niche.niche_name == "Tumor-Infiltrating Niche"

    fetched = await repo.get_session(session.id)
    assert fetched is not None
    assert len(fetched.deconvolutions) == 1
    assert len(fetched.niche_boundaries) == 1
