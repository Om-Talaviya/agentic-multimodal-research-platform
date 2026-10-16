"""Tests for Phase 571: Autonomous High-Plex Microfluidic Spatial In-Situ CUT&Tag Chromatin Modification Niche Profiler repository."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from database.connection import Base
from database.repositories.single_cell_spatial_epigenomic_cut_and_tag_repo import SingleCellSpatialEpigenomicCutAndTagRepository


@pytest_asyncio.fixture
async def async_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_single_cell_spatial_epigenomic_cut_and_tag_repository(async_session: AsyncSession):
    repo = SingleCellSpatialEpigenomicCutAndTagRepository(async_session)

    study = await repo.create_study(
        name="Autonomous High-Plex Microfluidic Spatial In-Situ CUT&Tag Chromatin Modification Niche Profiler Benchmark",
        target_specimen="Murine Embryonic Cortex Cryosection Microfluidic Deterministic Barcoding CUT&Tag for H3K27me3 and H3K4me3",
        analytical_modality="spatial-cut-and-tag-epigenomics",
        chromatin_enrichment_specificity=9.4,
        spatial_barcoding_purity=0.975,
        signal_to_background_promoter_ratio=18.2,
        niche_clustering_silhouette=0.885,
        confidence_score=0.994,
        status="completed",
        summary_report="Automated validation benchmark passed successfully.",
    )
    assert study.id is not None
    assert study.name == "Autonomous High-Plex Microfluidic Spatial In-Situ CUT&Tag Chromatin Modification Niche Profiler Benchmark"
    assert study.chromatin_enrichment_specificity == 9.4
    assert study.confidence_score == 0.994

    profile = await repo.add_item_profile(
        study_id=study.id,
        item_name="Spatial_Chromatin_Domain_Epigenetic_Cluster",
        quantitative_value=9.4,
        profile_category="Primary Profile",
        log2_fold_change=1.85,
        significance_score=0.98,
    )
    assert profile.id is not None
    assert profile.study_id == study.id
    assert profile.item_name == "Spatial_Chromatin_Domain_Epigenetic_Cluster"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="chromatin_enrichment_specificity",
        observed_value=9.4,
        z_score=2.85,
        p_value=0.001,
    )
    assert trace.id is not None
    assert trace.study_id == study.id

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.id == study.id

    studies = await repo.list_studies()
    assert len(studies) >= 1
