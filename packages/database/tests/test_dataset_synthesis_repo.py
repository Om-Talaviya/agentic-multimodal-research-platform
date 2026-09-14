import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from database.connection import Base
from database.models.dataset_synthesis import (
    DBAlignmentExport,
    DBInstructionSample,
    DBSyntheticDataset,
)
from database.repositories.dataset_synthesis_repo import DatasetSynthesisRepository


@pytest.fixture
async def db_session():
    """Create in-memory SQLite database session for testing."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_factory = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session_factory() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_dataset_synthesis_repo_full_lifecycle(db_session: AsyncSession):
    """Test full Synthetic Dataset, Instruction Sample, and Alignment Export lifecycle."""
    repo = DatasetSynthesisRepository(db_session)
    user_id = uuid.uuid4()

    # 1. Create Dataset
    dataset = DBSyntheticDataset(
        user_id=user_id,
        name="Quantum Circuit Alignment SFT",
        description="Fine-tuning dataset for variational quantum ansatzes.",
        dataset_format="alpaca_sft",
        domain_field="quantum_computing",
        target_model_family="llama_3",
        status="synthesizing",
    )
    created_dataset = await repo.create_dataset(dataset)
    assert created_dataset.id is not None
    assert created_dataset.name == "Quantum Circuit Alignment SFT"
    assert created_dataset.total_samples == 0

    # 2. Get Dataset
    fetched = await repo.get_dataset(created_dataset.id)
    assert fetched is not None
    assert len(fetched.samples) == 0

    # 3. Add Instruction Sample
    sample1 = DBInstructionSample(
        dataset_id=created_dataset.id,
        sample_index=1,
        system_prompt="You are a quantum computing specialist.",
        instruction="Derive the gradient scaling for QAOA layer depth $p=4$.",
        input_context="Hardware: Trapped Ion",
        chosen_response="Gradient variance scales as $\\Omega(1/\\text{poly}(N))$ with local cost observables.",
        cot_reasoning_trace="Step 1: Compute Pauli expectation value.\nStep 2: Apply Lie algebra commutation relations.",
        evolution_strategy="in_depth_expansion",
        quality_score=0.95,
        curation_verdict="accepted",
    )
    added_sample1 = await repo.add_sample(sample1)
    assert added_sample1.id is not None

    # 4. Batch Add Samples
    sample2 = DBInstructionSample(
        dataset_id=created_dataset.id,
        sample_index=2,
        instruction="Contrast QAOA against simulated annealing on Max-Cut.",
        chosen_response="QAOA exhibits polynomial sampling speedup on 3-regular graph topologies.",
        rejected_response="Simulated annealing is always better.",
        evolution_strategy="adversarial_redteaming",
        quality_score=0.92,
        curation_verdict="accepted",
    )
    batch_count = await repo.batch_add_samples(created_dataset.id, [sample2])
    assert batch_count == 1

    # 5. List Datasets
    datasets = await repo.list_datasets(user_id=user_id)
    assert len(datasets) == 1

    # 6. Active Learning Curation
    curated = await repo.update_sample_curation(
        sample_id=added_sample1.id,
        verdict="edited",
        quality_score=0.98,
        chosen_response="Refined: Gradient variance scales as $\\Omega(1/\\text{poly}(N))$ under local observables with non-vanishing signal.",
    )
    assert curated is not None
    assert curated.curation_verdict == "edited"
    assert curated.quality_score == 0.98

    # 7. Record Export
    export = DBAlignmentExport(
        dataset_id=created_dataset.id,
        export_format="jsonl",
        sample_count=2,
        file_size_bytes=1024,
    )
    created_export = await repo.record_export(export)
    assert created_export.id is not None

    # 8. Metrics
    metrics = await repo.get_synthesis_metrics()
    assert metrics["total_synthetic_datasets"] == 1
    assert metrics["total_instruction_samples"] == 2
    assert metrics["total_alignment_exports"] == 1
    assert metrics["average_quality_score"] > 0.90

    # 9. Delete Dataset
    assert await repo.delete_dataset(created_dataset.id) is True
    assert await repo.get_dataset(created_dataset.id) is None
