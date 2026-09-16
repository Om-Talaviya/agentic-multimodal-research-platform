"""
REST API routes for Autonomous Electronic Lab Notebook (ELN) (Phase 53).
Provides notebook creation, multimodal block appending/updating, and 21 CFR Part 11 digital signatures.
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db_session
from database.repositories.eln_repo import LabNotebookRepository
from research.eln.eln_engine import ElectronicLabNotebookEngine

router = APIRouter(prefix="/eln", tags=["Electronic Lab Notebook (ELN)"])
engine = ElectronicLabNotebookEngine()


# ---------------------------------------------------------------------------
# Pydantic Request & Response Schemas
# ---------------------------------------------------------------------------

class NotebookCreateRequest(BaseModel):
    title: str = Field(..., example="CRISPR Exon 20 Knock-in Protocol & Observation Log")
    author_id: str = Field("dr_jane_doe", example="dr_jane_doe")
    project_id: Optional[str] = Field(None, example="proj-crispr-2026")
    tags: List[str] = Field(default_factory=lambda: ["CRISPR", "Exon20", "In-Vitro"])


class BlockCreateRequest(BaseModel):
    block_type: str = Field(..., example="PROTOCOL_STEP")
    content_json: Dict[str, Any] = Field(
        ...,
        example={
            "step_number": 1,
            "title": "Cell Seeding & Ribonucleoprotein Transfection",
            "instructions": "Seed HEK293T cells at 2.5e5 cells/well in a 24-well plate. Incubate 24h at 37C with 5% CO2.",
            "parameters": {"temperature_c": 37.0, "co2_percent": 5.0, "incubation_hours": 24.0},
        }
    )
    actor_id: str = Field("dr_jane_doe", example="dr_jane_doe")


class BlockUpdateRequest(BaseModel):
    content_json: Dict[str, Any] = Field(...)
    actor_id: str = Field("dr_jane_doe", example="dr_jane_doe")


class WitnessSignRequest(BaseModel):
    witness_id: str = Field(..., example="dr_senior_pi")
    witness_statement: str = Field(
        ...,
        example="I have reviewed and witnessed the experimental steps and protocol execution described herein."
    )


# ---------------------------------------------------------------------------
# API Routes
# ---------------------------------------------------------------------------

@router.post("/notebooks", status_code=status.HTTP_201_CREATED)
async def create_notebook(
    req: NotebookCreateRequest,
    db: AsyncSession = Depends(get_db_session),
):
    """Create a new ELN notebook."""
    repo = LabNotebookRepository(db)
    notebook = await repo.create_notebook(
        title=req.title,
        author_id=req.author_id,
        project_id=req.project_id,
        tags=req.tags,
    )
    return notebook


@router.get("/notebooks")
async def list_notebooks(
    status_filter: Optional[str] = None,
    author_id: Optional[str] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db_session),
):
    """List all lab notebooks."""
    repo = LabNotebookRepository(db)
    notebooks = await repo.list_notebooks(status=status_filter, author_id=author_id, limit=limit)
    response_list = []
    for nb in notebooks:
        blocks = await repo.list_blocks(nb.id)
        response_list.append({
            "id": nb.id,
            "title": nb.title,
            "author_id": nb.author_id,
            "project_id": nb.project_id,
            "status": nb.status,
            "tags": nb.tags,
            "cfr_part11_signed": nb.cfr_part11_signed,
            "witness_signature": nb.witness_signature,
            "created_at": nb.created_at.isoformat() if nb.created_at else None,
            "updated_at": nb.updated_at.isoformat() if nb.updated_at else None,
            "blocks_count": len(blocks),
        })
    return response_list


@router.get("/notebooks/{notebook_id}")
async def get_notebook(
    notebook_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Get full notebook with sequential blocks and immutable audit trail."""
    repo = LabNotebookRepository(db)
    notebook = await repo.get_notebook(notebook_id)
    if not notebook:
        raise HTTPException(status_code=404, detail="Lab notebook not found.")

    blocks = await repo.list_blocks(notebook_id)
    audit_trails = await repo.list_audit_trails(notebook_id)

    return {
        "id": notebook.id,
        "title": notebook.title,
        "author_id": notebook.author_id,
        "project_id": notebook.project_id,
        "status": notebook.status,
        "tags": notebook.tags,
        "cfr_part11_signed": notebook.cfr_part11_signed,
        "witness_signature": notebook.witness_signature,
        "created_at": notebook.created_at.isoformat() if notebook.created_at else None,
        "updated_at": notebook.updated_at.isoformat() if notebook.updated_at else None,
        "blocks": [
            {
                "id": b.id,
                "notebook_id": b.notebook_id,
                "block_type": b.block_type,
                "order_index": b.order_index,
                "content_json": b.content_json,
                "created_at": b.created_at.isoformat() if b.created_at else None,
            }
            for b in blocks
        ],
        "audit_trails": [
            {
                "id": a.id,
                "actor_id": a.actor_id,
                "action": a.action,
                "diff_payload": a.diff_payload,
                "cryptographic_hash": a.cryptographic_hash,
                "timestamp": a.timestamp.isoformat() if a.timestamp else None,
            }
            for a in audit_trails
        ],
    }


@router.post("/notebooks/{notebook_id}/blocks", status_code=status.HTTP_201_CREATED)
async def add_block(
    notebook_id: str,
    req: BlockCreateRequest,
    db: AsyncSession = Depends(get_db_session),
):
    """Append a validated multimodal content block to the notebook."""
    repo = LabNotebookRepository(db)
    notebook = await repo.get_notebook(notebook_id)
    if not notebook:
        raise HTTPException(status_code=404, detail="Lab notebook not found.")

    validated_content = engine.validate_block_content(
        block_type=req.block_type,
        content=req.content_json,
    )

    block = await repo.add_block(
        notebook_id=notebook_id,
        block_type=req.block_type,
        content_json=validated_content,
        actor_id=req.actor_id,
    )
    return block


@router.put("/notebooks/{notebook_id}/blocks/{block_id}", status_code=status.HTTP_200_OK)
async def update_block(
    notebook_id: str,
    block_id: str,
    req: BlockUpdateRequest,
    db: AsyncSession = Depends(get_db_session),
):
    """Update block content and log cryptographic audit trail."""
    repo = LabNotebookRepository(db)
    block = await repo.update_block(
        block_id=block_id,
        content_json=req.content_json,
        actor_id=req.actor_id,
    )
    if not block:
        raise HTTPException(status_code=404, detail="Block not found.")
    return block


@router.post("/notebooks/{notebook_id}/sign", status_code=status.HTTP_200_OK)
async def sign_notebook(
    notebook_id: str,
    req: WitnessSignRequest,
    db: AsyncSession = Depends(get_db_session),
):
    """Apply 21 CFR Part 11 compliant digital witness signature."""
    repo = LabNotebookRepository(db)
    notebook = await repo.witness_sign(
        notebook_id=notebook_id,
        witness_id=req.witness_id,
        witness_statement=req.witness_statement,
    )
    if not notebook:
        raise HTTPException(status_code=404, detail="Lab notebook not found.")
    return {
        "status": "WITNESSED",
        "cfr_part11_signed": True,
        "witness_signature": notebook.witness_signature,
    }


@router.get("/metrics")
async def get_eln_metrics(
    db: AsyncSession = Depends(get_db_session),
):
    """Get ELN compliance and storage metrics."""
    repo = LabNotebookRepository(db)
    return await repo.get_metrics()
