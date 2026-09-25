"""Tests for Spatial Proteogenomics Repository."""

import pytest
from database.connection import AsyncSession
from database.repositories.spatial_proteogenomics_repo import SpatialProteogenomicsRepository


@pytest.mark.asyncio
async def test_spatial_proteogenomics_repo_crud(db_session: AsyncSession) -> None:
    repo = SpatialProteogenomicsRepository(db_session)

    study = await repo.create_study(
        study_name="Test Glioblastoma CITE-seq",
        tissue_sample_id="GBM_TME_Slice_04",
        total_spots_analyzed=1,
        mean_pearson_colocalization_r=0.91,
        subcellular_niche_count=1,
        summary_metrics={"score": 0.91},
        spots=[
            {
                "spot_barcode": "SPOT_A1_001",
                "x_coord": 124.5,
                "y_coord": 450.2,
                "target_mrna_symbol": "EGFR",
                "mrna_normalized_count": 48.2,
                "target_protein_antibody": "Total-EGFR (Clone D38B1)",
                "protein_adt_signal": 1420.0,
                "colocalization_pearson_r": 0.91,
                "subcellular_niche": "Invasive Tumor Core",
            }
        ],
        enrichment_metrics=[
            {
                "marker_pair": "EGFR (mRNA) / EGFR (Protein)",
                "enrichment_z_score": 4.82,
                "fdr_q_value": 0.0001,
                "biological_relevance": "High Receptor Density",
            }
        ],
    )

    assert study.id is not None
    assert study.study_name == "Test Glioblastoma CITE-seq"
    assert len(study.spots) == 1
    assert len(study.enrichment_metrics) == 1

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.tissue_sample_id == "GBM_TME_Slice_04"

    studies = await repo.list_studies()
    assert len(studies) >= 1

    deleted = await repo.delete_study(study.id)
    assert deleted is True

    empty = await repo.get_study(study.id)
    assert empty is None
