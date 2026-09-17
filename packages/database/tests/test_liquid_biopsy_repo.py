"""Tests for Liquid Biopsy repository."""
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from database.connection import Base
from database.repositories.liquid_biopsy_repo import LiquidBiopsyRepository


@pytest.fixture
async def async_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_factory = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session_factory() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_create_and_get_sample(async_session: AsyncSession):
    repo = LiquidBiopsyRepository(async_session)

    sample = await repo.create_sample(
        patient_id="PT-CRC-99",
        sample_barcode="LB-99-A",
        cancer_type="Colorectal Cancer",
        sampling_timepoint="POST_SURGERY",
        total_cfdna_ng_ml=15.0,
        tumor_fraction_pct=2.5,
        mrd_status="MRD_POSITIVE",
        fragment_short_ratio=0.35,
        median_fragment_length_bp=166,
    )

    assert sample.id is not None
    assert sample.patient_id == "PT-CRC-99"

    fetched = await repo.get_sample(sample.id)
    assert fetched is not None
    assert fetched.tumor_fraction_pct == 2.5


@pytest.mark.asyncio
async def test_add_distributions_and_motifs(async_session: AsyncSession):
    repo = LiquidBiopsyRepository(async_session)

    sample = await repo.create_sample(
        patient_id="PT-NSCLC-01",
        sample_barcode="LB-01-B",
        cancer_type="Lung Cancer",
        sampling_timepoint="BASELINE",
        total_cfdna_ng_ml=22.0,
        tumor_fraction_pct=5.0,
        mrd_status="MRD_POSITIVE",
        fragment_short_ratio=0.42,
        median_fragment_length_bp=164,
    )

    distributions_data = [
        {"bin_start_bp": 100, "bin_end_bp": 150, "fragment_count": 25000, "fragment_frequency_pct": 25.0},
        {"bin_start_bp": 151, "bin_end_bp": 175, "fragment_count": 50000, "fragment_frequency_pct": 50.0},
    ]

    bins = await repo.add_size_distributions(sample.id, distributions_data)
    assert len(bins) == 2

    motifs_data = [
        {"motif_sequence_4mer": "CCCA", "observed_frequency": 0.089, "reference_frequency": 0.0625, "motif_diversity_score": 1.42},
        {"motif_sequence_4mer": "CCAG", "observed_frequency": 0.081, "reference_frequency": 0.0625, "motif_diversity_score": 1.30},
    ]

    motifs = await repo.add_end_motifs(sample.id, motifs_data)
    assert len(motifs) == 2

    fetched_bins = await repo.get_size_distributions_by_sample(sample.id)
    assert len(fetched_bins) == 2

    fetched_motifs = await repo.get_end_motifs_by_sample(sample.id)
    assert len(fetched_motifs) == 2
