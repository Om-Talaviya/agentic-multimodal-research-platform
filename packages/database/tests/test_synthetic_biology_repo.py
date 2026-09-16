"""
Tests for Phase 65: Synthetic Biology Database Repository.
"""
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from database.connection import Base
from database.repositories.synthetic_biology_repo import SyntheticBiologyRepository


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
async def test_synbio_repo_crud(async_session: AsyncSession):
    repo = SyntheticBiologyRepository(async_session)

    # 1. Create Circuit
    circuit = await repo.create_circuit(
        circuit_name="Test AND Gate",
        logic_expression="A AND B",
    )
    assert circuit.id is not None

    # 2. Add Parts & Truth Table
    updated = await repo.add_parts_and_truth_table(
        circuit_id=circuit.id,
        parts_data=[
            {"part_type": "Promoter", "part_name": "pTac", "part_sequence": "ATGC"}
        ],
        truth_table_data=[
            {"input_state_a": True, "input_state_b": True, "expected_output": True, "simulated_fluorescence_rfu": 4500.0}
        ],
        on_off_ratio=50.0,
    )
    assert updated is not None
    assert updated.total_parts == 1
    assert len(updated.parts) == 1
    assert len(updated.truth_table) == 1
