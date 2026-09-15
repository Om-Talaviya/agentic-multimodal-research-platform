"""Unit tests for Spatial Transcriptomics Repository (Phase 42)."""
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from database.connection import Base
from database.repositories.spatial_repo import SpatialTranscriptomicsRepository

@pytest.fixture
async def async_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session_factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session_factory() as session:
        yield session
    
    await engine.dispose()

@pytest.mark.asyncio
async def test_spatial_repository_crud(async_session: AsyncSession):
    repo = SpatialTranscriptomicsRepository(async_session)

    # 1. Create dataset
    dataset = await repo.create_dataset(
        title="Human Glioblastoma Spatial Microenvironment",
        tissue_type="Glioblastoma",
        technology="10x Visium",
        slide_width_um=6500.0,
    )
    assert dataset.id is not None
    assert dataset.title == "Human Glioblastoma Spatial Microenvironment"
    assert dataset.tissue_type == "Glioblastoma"

    # 2. Add spots
    spots_data = [
        {
            "spot_barcode": "AAACAAC-01-01-1",
            "x_coord": 2450.0,
            "y_coord": 2510.0,
            "cluster_id": 1,
            "cluster_name": "Tumor Core",
            "cell_type_annotation": "Tumor Core",
            "total_counts": 4200,
            "n_genes_detected": 1500,
            "tumor_proximity_score": 0.98,
        },
        {
            "spot_barcode": "AAACAAC-01-02-1",
            "x_coord": 3800.0,
            "y_coord": 3850.0,
            "cluster_id": 3,
            "cluster_name": "Cancer-Associated Stroma",
            "cell_type_annotation": "Cancer-Associated Stroma",
            "total_counts": 3100,
            "n_genes_detected": 1100,
            "tumor_proximity_score": 0.25,
        }
    ]
    n_added = await repo.add_spots(dataset.id, spots_data)
    assert n_added == 2

    # Query spots
    spots = await repo.get_spots(dataset.id)
    assert len(spots) == 2
    assert spots[0].cluster_name == "Tumor Core"

    # 3. Add communications
    comms_data = [
        {
            "pathway_name": "VEGF",
            "ligand_gene": "VEGFA",
            "receptor_gene": "FLT1",
            "source_cluster": "Tumor Core",
            "target_cluster": "Invasive Margin",
            "communication_score": 0.945,
            "p_value": 0.0001,
            "interaction_distance_um": 65.0,
        }
    ]
    await repo.add_communications(dataset.id, comms_data)
    comms = await repo.get_communications(dataset.id)
    assert len(comms) == 1
    assert comms[0].ligand_gene == "VEGFA"
    assert comms[0].communication_score == 0.945

    # 4. Add domains
    domains_data = [
        {
            "domain_name": "Tumor Core",
            "domain_type": "tumor",
            "color_hex": "#ef4444",
            "spot_count": 1,
            "area_percentage": 50.0,
            "top_marker_genes": ["MKI67", "EGFR"],
        }
    ]
    await repo.add_domains(dataset.id, domains_data)
    domains = await repo.get_domains(dataset.id)
    assert len(domains) == 1
    assert domains[0].domain_name == "Tumor Core"

    # 5. List and Delete
    datasets = await repo.list_datasets(tissue_type="Glioblastoma")
    assert len(datasets) == 1

    deleted = await repo.delete_dataset(dataset.id)
    assert deleted is True
    assert await repo.get_dataset(dataset.id) is None
