"""
Tests for Phase 56: Epigenomics Database Repository.
"""
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from database.connection import Base
from database.repositories.epigenomics_repo import EpigenomicsRepository


@pytest.fixture
async def async_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_factory = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    async with async_session_factory() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_epigenomics_repo_crud(async_session: AsyncSession):
    repo = EpigenomicsRepository(async_session)

    # 1. Create experiment
    exp = await repo.create_experiment(
        sample_id="SAM-ATAC-TEST-01",
        tissue_type="T-Cell",
        assay_type="ATAC-seq",
    )
    assert exp.id is not None

    # 2. Add Peaks with Motifs
    peaks = await repo.add_peaks_with_motifs(
        experiment_id=exp.id,
        peaks_data=[
            {
                "chromosome": "chr1",
                "start_pos": 1000000,
                "end_pos": 1000500,
                "peak_score": 250.0,
                "fold_enrichment": 12.5,
                "p_value_neg_log10": 20.0,
                "genomic_annotation": "Promoter",
                "nearest_gene": "PDCD1",
                "motifs": [
                    {"motif_name": "NFKB1", "pwm_match_score": 0.94}
                ],
            }
        ],
    )
    assert len(peaks) == 1

    # 3. Query Experiment
    fetched = await repo.get_experiment(exp.id)
    assert fetched is not None
    assert fetched.total_peaks_called == 1
    assert len(fetched.peaks[0].motifs) == 1

    # 4. Query Peaks with filter
    filtered = await repo.query_peaks(exp.id, chromosome="chr1")
    assert len(filtered) == 1
