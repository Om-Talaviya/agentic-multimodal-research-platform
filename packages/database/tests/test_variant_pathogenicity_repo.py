"""Tests for Genomic Variant Pathogenicity repository."""
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from database.connection import Base
from database.repositories.variant_pathogenicity_repo import VariantPathogenicityRepository


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
async def test_create_and_get_variant_report(async_session: AsyncSession):
    repo = VariantPathogenicityRepository(async_session)

    report = await repo.create_report(
        gene_symbol="BRCA1",
        hgvs_c="c.5266dupC",
        hgvs_p="p.Gln1756Profs*74",
        chromosome="chr17",
        genomic_position=43044295,
        ref_allele="C",
        alt_allele="CC",
        transcript_id="NM_007294.4",
        acmg_class="PATHOGENIC",
        pathogenicity_score=0.99,
        total_criteria_met=4,
        clinvar_id="VCV000017667",
    )

    assert report.id is not None
    assert report.gene_symbol == "BRCA1"
    assert report.acmg_class == "PATHOGENIC"

    fetched = await repo.get_report(report.id)
    assert fetched is not None
    assert fetched.hgvs_p == "p.Gln1756Profs*74"


@pytest.mark.asyncio
async def test_add_criteria_and_predictors(async_session: AsyncSession):
    repo = VariantPathogenicityRepository(async_session)

    report = await repo.create_report(
        gene_symbol="TP53",
        hgvs_c="c.743G>A",
        hgvs_p="p.Arg248Gln",
        chromosome="chr17",
        genomic_position=7673802,
        ref_allele="G",
        alt_allele="A",
        transcript_id="NM_000546.6",
        acmg_class="PATHOGENIC",
        pathogenicity_score=0.98,
        total_criteria_met=3,
    )

    criteria_data = [
        {
            "criterion_code": "PS3",
            "criterion_type": "PATHOGENIC_STRONG",
            "status": "MET",
            "weight": 4.0,
            "rationale": "Loss of transactivation function in yeast/mammalian assays.",
            "evidence_source": "Functional Assay",
        },
        {
            "criterion_code": "PM1",
            "criterion_type": "PATHOGENIC_MODERATE",
            "status": "MET",
            "weight": 2.0,
            "rationale": "DNA-binding domain hotspot.",
            "evidence_source": "UniProt",
        }
    ]

    criteria = await repo.add_criteria(report.id, criteria_data)
    assert len(criteria) == 2

    predictors_data = [
        {
            "tool_name": "AlphaMissense",
            "score_value": 0.99,
            "score_percentile": 99.0,
            "prediction_label": "Pathogenic",
        },
        {
            "tool_name": "CADD",
            "score_value": 32.0,
            "score_percentile": 99.5,
            "prediction_label": "Deleterious",
        }
    ]

    scores = await repo.add_predictor_scores(report.id, predictors_data)
    assert len(scores) == 2

    fetched_crit = await repo.get_criteria_by_report(report.id)
    assert len(fetched_crit) == 2

    fetched_scores = await repo.get_predictor_scores_by_report(report.id)
    assert len(fetched_scores) == 2
