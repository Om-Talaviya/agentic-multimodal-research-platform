"""
Unit tests for Phase 110: Survival Prognosis Repository.
"""
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from database.connection import Base
from database.repositories.survival_prognosis_repo import SurvivalPrognosisRepository

@pytest.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.mark.asyncio
async def test_survival_prognosis_repo_crud(db_session):
    repo = SurvivalPrognosisRepository(db_session)

    model = await repo.create_model(
        model_name="Test-Prognostic-Model",
        cancer_cohort="TCGA-LUAD",
        c_index_score=0.84,
        hazard_ratio_high_vs_low=3.82,
        log_rank_p_value=0.0001,
        risk_stratification_method="Cox-Proportional-Hazards",
        features_weights={"TP53": 0.85, "EGFR": -0.62}
    )

    assert model.id is not None
    assert model.model_name == "Test-Prognostic-Model"
    assert model.c_index_score == 0.84

    patient = await repo.add_patient(
        model_id=model.id,
        patient_barcode="TCGA-LUAD-PT-001",
        overall_survival_months=18.5,
        vital_status=1,
        risk_group="HIGH",
        risk_score=1.45,
        biomarker_vector={"TP53": 1}
    )

    assert patient.id is not None
    assert patient.patient_barcode == "TCGA-LUAD-PT-001"

    curve = await repo.add_curve(
        model_id=model.id,
        risk_tier="HIGH",
        time_points_months=[0.0, 12.0, 24.0, 36.0],
        survival_probability_km=[1.0, 0.65, 0.40, 0.20],
        patients_at_risk=[50, 32, 20, 10],
        median_survival_months=18.5
    )

    assert curve.id is not None
    assert curve.risk_tier == "HIGH"

    patients = await repo.list_patients(model.id)
    curves = await repo.list_curves(model.id)
    assert len(patients) == 1
    assert len(curves) == 1
