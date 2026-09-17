"""Tests for Chemogenomics Polypharmacology repository."""
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from database.connection import Base
from database.repositories.chemogenomics_repo import ChemogenomicsRepository


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
async def test_create_and_get_profile(async_session: AsyncSession):
    repo = ChemogenomicsRepository(async_session)

    profile = await repo.create_profile(
        compound_name="Imatinib",
        smiles="CC1=C(C=C(C=C1)NC(=O)C2=CC=C(C=C2)CN3CCN(CC3)C)NC4=NC=CC(=N4)C5=CN=CC=C5",
        primary_target="ABL1",
        gini_selectivity_index=0.68,
        selectivity_tier="FAMILY_SELECTIVE",
        total_targets_screened=50,
        off_target_liabilities_count=0,
    )

    assert profile.id is not None
    assert profile.compound_name == "Imatinib"

    fetched = await repo.get_profile(profile.id)
    assert fetched is not None
    assert fetched.primary_target == "ABL1"


@pytest.mark.asyncio
async def test_add_affinities_and_alerts(async_session: AsyncSession):
    repo = ChemogenomicsRepository(async_session)

    profile = await repo.create_profile(
        compound_name="Sunitinib",
        smiles="CCN(CC)CCNC(=O)C1=C(NC(=C1C)C=C2C3=C(C=CC(=C3)F)NC2=O)C",
        primary_target="VEGFR2",
        gini_selectivity_index=0.32,
        selectivity_tier="PAN_INHIBITOR",
    )

    affinities_data = [
        {"target_gene": "KDR", "uniprot_id": "P35968", "protein_family": "KINASE", "affinity_type": "IC50", "affinity_value_nm": 9.0, "is_primary_target": True},
        {"target_gene": "FLT3", "uniprot_id": "P36888", "protein_family": "KINASE", "affinity_type": "IC50", "affinity_value_nm": 25.0, "is_primary_target": False},
    ]

    affinities = await repo.add_affinities(profile.id, affinities_data)
    assert len(affinities) == 2

    alerts_data = [
        {
            "target_gene": "KCNH2",
            "risk_type": "CARDIOTOXICITY_HERG",
            "binding_potency_nm": 850.0,
            "severity": "HIGH",
            "recommendation": "Monitor QTc prolongation.",
        }
    ]

    alerts = await repo.add_alerts(profile.id, alerts_data)
    assert len(alerts) == 1

    fetched_affinities = await repo.get_affinities_by_profile(profile.id)
    assert len(fetched_affinities) == 2

    fetched_alerts = await repo.get_alerts_by_profile(profile.id)
    assert len(fetched_alerts) == 1
