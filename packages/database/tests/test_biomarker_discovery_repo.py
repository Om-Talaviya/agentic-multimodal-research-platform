"""Tests for Multi-Modal Biomarker Discovery repository."""
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from database.connection import Base
from database.repositories.biomarker_discovery_repo import BiomarkerDiscoveryRepository


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
async def test_create_and_get_study(async_session: AsyncSession):
    repo = BiomarkerDiscoveryRepository(async_session)

    study = await repo.create_study(
        study_title="Pan-Cancer Checkpoint Signature",
        disease_indication="Melanoma & NSCLC",
        cohort_sample_size=150,
        omics_layers_json=["TRANSCRIPTOMICS", "PROTEOMICS", "METABOLOMICS"],
        signature_stability_score=0.88,
        auc_roc_score=0.93,
    )

    assert study.id is not None
    assert study.study_title == "Pan-Cancer Checkpoint Signature"

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.disease_indication == "Melanoma & NSCLC"


@pytest.mark.asyncio
async def test_add_features_and_stratifications(async_session: AsyncSession):
    repo = BiomarkerDiscoveryRepository(async_session)

    study = await repo.create_study(
        study_title="Breast Cancer Multi-Omics Signature",
        disease_indication="Triple-Negative Breast Cancer (TNBC)",
    )

    features_data = [
        {
            "feature_name": "CXCL9",
            "omics_modality": "TRANSCRIPTOMICS",
            "log2_fold_change": 3.1,
            "adjusted_p_value": 0.0001,
            "feature_importance_weight": 0.92,
            "correlation_direction": "POSITIVE",
        },
        {
            "feature_name": "CD274",
            "omics_modality": "PROTEOMICS",
            "log2_fold_change": 2.4,
            "adjusted_p_value": 0.0005,
            "feature_importance_weight": 0.86,
            "correlation_direction": "POSITIVE",
        },
    ]

    features = await repo.add_features(study.id, features_data)
    assert len(features) == 2

    stratifications_data = [
        {
            "patient_cohort_id": "Cohort-A",
            "prognostic_risk_tier": "LOW",
            "response_probability_score": 0.85,
            "composite_signature_score": 2.1,
            "signature_expression_map_json": {"CXCL9": 3.1},
        }
    ]

    stratifications = await repo.add_stratifications(study.id, stratifications_data)
    assert len(stratifications) == 1

    fetched_features = await repo.get_features_by_study(study.id)
    assert len(fetched_features) == 2

    fetched_stratifications = await repo.get_stratifications_by_study(study.id)
    assert len(fetched_stratifications) == 1
