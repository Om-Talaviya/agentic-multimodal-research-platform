"""Tests for LNP Formulation & Membrane Dynamics repository."""
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from database.connection import Base
from database.repositories.lnp_formulation_repo import LNPFormulationRepository


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
async def test_create_and_get_formulation(async_session: AsyncSession):
    repo = LNPFormulationRepository(async_session)

    study = await repo.create_formulation(
        formulation_name="mRNA Vaccine Formulation A",
        cargo_type="mRNA",
        ionizable_lipid_name="SM-102",
        np_ratio=6.0,
        encapsulation_efficiency_pct=95.2,
        mean_diameter_nm=75.0,
        pdi_polydispersity_index=0.11,
        zeta_potential_mv=2.8,
        apparent_pka=6.68,
    )

    assert study.id is not None
    assert study.formulation_name == "mRNA Vaccine Formulation A"

    fetched = await repo.get_formulation(study.id)
    assert fetched is not None
    assert fetched.ionizable_lipid_name == "SM-102"


@pytest.mark.asyncio
async def test_add_components_and_membrane_profile(async_session: AsyncSession):
    repo = LNPFormulationRepository(async_session)

    study = await repo.create_formulation(
        formulation_name="siRNA Liver Delivery LNP",
        cargo_type="siRNA",
        ionizable_lipid_name="MC3",
    )

    components_data = [
        {
            "component_name": "DLin-MC3-DMA",
            "lipid_category": "IONIZABLE_LIPID",
            "molar_percentage": 50.0,
            "molecular_weight_g_mol": 642.1,
            "charge_at_ph7": 0.0,
        },
        {
            "component_name": "DSPC",
            "lipid_category": "HELPER_LIPID",
            "molar_percentage": 10.0,
            "molecular_weight_g_mol": 790.2,
            "charge_at_ph7": 0.0,
        },
    ]

    components = await repo.add_components(study.id, components_data)
    assert len(components) == 2

    profile_data = {
        "membrane_thickness_angstrom": 38.8,
        "area_per_lipid_angstrom2": 63.2,
        "order_parameter_s2": 0.24,
        "bending_modulus_kc_kbt": 25.0,
        "endosomal_escape_efficiency_pct": 21.0,
        "cytotoxicity_score": 0.12,
    }

    profile = await repo.add_membrane_profile(study.id, profile_data)
    assert profile.id is not None
    assert profile.membrane_thickness_angstrom == 38.8

    fetched_components = await repo.get_components_by_formulation(study.id)
    assert len(fetched_components) == 2

    fetched_profile = await repo.get_membrane_profile_by_formulation(study.id)
    assert fetched_profile is not None
    assert fetched_profile.endosomal_escape_efficiency_pct == 21.0
