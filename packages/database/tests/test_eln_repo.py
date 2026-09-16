"""Unit tests for LabNotebookRepository (Phase 53)."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from database.connection import Base
from database.models.eln import (
    DBElectronicLabNotebook,
    DBLabNotebookBlock,
    DBELNAuditTrailEntry,
)
from database.repositories.eln_repo import LabNotebookRepository


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
async def test_eln_repo_lifecycle(db_session: AsyncSession):
    repo = LabNotebookRepository(db_session)

    # 1. Create Notebook
    notebook = await repo.create_notebook(
        title="Test CRISPR Knock-in Protocol",
        author_id="dr_tester",
        tags=["CRISPR", "Validation"],
    )
    assert notebook.id is not None
    assert notebook.title == "Test CRISPR Knock-in Protocol"
    assert notebook.status == "DRAFT"

    # 2. Add Protocol Step Block
    block1 = await repo.add_block(
        notebook_id=notebook.id,
        block_type="PROTOCOL_STEP",
        content_json={"step_number": 1, "title": "Electroporation", "parameters": {"voltage": 1150}},
        actor_id="dr_tester",
    )
    assert block1.id is not None
    assert block1.order_index == 1

    # 3. Add SMILES Block
    block2 = await repo.add_block(
        notebook_id=notebook.id,
        block_type="MOLECULAR_SMILES",
        content_json={"smiles": "CC(=O)Oc1ccccc1C(=O)O", "molecular_weight": 180.16},
        actor_id="dr_tester",
    )
    assert block2.id is not None
    assert block2.order_index == 2

    # 4. List Blocks
    blocks = await repo.list_blocks(notebook.id)
    assert len(blocks) == 2

    # 5. Update Block
    updated_block = await repo.update_block(
        block_id=block1.id,
        content_json={"step_number": 1, "title": "Updated Electroporation", "parameters": {"voltage": 1200}},
        actor_id="dr_tester",
    )
    assert updated_block.content_json["parameters"]["voltage"] == 1200

    # 6. Apply 21 CFR Part 11 Witness Signature
    signed_nb = await repo.witness_sign(
        notebook_id=notebook.id,
        witness_id="dr_principal_investigator",
        witness_statement="Verified experimental observations.",
    )
    assert signed_nb.cfr_part11_signed is True
    assert signed_nb.status == "WITNESSED"
    assert "sha256_hash" in signed_nb.witness_signature

    # 7. Verify Audit Trails
    audits = await repo.list_audit_trails(notebook.id)
    assert len(audits) >= 4  # CREATE + 2 INSERTS + 1 UPDATE + 1 SIGN

    # 8. Metrics
    metrics = await repo.get_metrics()
    assert metrics["total_notebooks"] == 1
    assert metrics["witnessed_notebooks"] == 1
    assert metrics["total_blocks"] == 2
