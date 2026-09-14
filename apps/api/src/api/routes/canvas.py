"""REST API routes for Real-Time Multi-Agent Collaborative Research Canvas & Visual Ideation Studio."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user, get_db_session
from database.models.canvas import DBCanvasBoard, DBCanvasEdge, DBCanvasNode
from database.repositories.canvas_repo import CanvasRepository
from research.canvas.ideation import CanvasIdeationEngine
from shared.auth import User
from shared.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/canvas", tags=["canvas"])


# ---------------- Request & Response Schemas ----------------

class CreateCanvasBoardPayload(BaseModel):
    title: str = Field(..., min_length=3, max_length=512)
    description: Optional[str] = None
    background_grid: str = Field(default="dots", pattern="^(dots|lines|crosses|clean)$")
    workspace_id: Optional[uuid.UUID] = None
    project_id: Optional[uuid.UUID] = None
    research_job_id: Optional[uuid.UUID] = None


class GenerateCanvasFromResearchPayload(BaseModel):
    title: str = Field(..., min_length=3)
    objective: str = Field(default="")
    findings: List[Dict[str, Any]] = Field(default_factory=list)
    evidence: List[Dict[str, Any]] = Field(default_factory=list)
    conclusions: List[str] = Field(default_factory=list)


class AddCanvasNodePayload(BaseModel):
    node_type: str = Field(default="hypothesis", pattern="^(hypothesis|evidence|paper|agent_thought|data_series|conclusion|counter_claim)$")
    title: str = Field(..., min_length=2, max_length=512)
    content: Optional[str] = None
    confidence_score: float = Field(default=0.85, ge=0.0, le=1.0)
    status: str = Field(default="verified")
    position_x: float = Field(default=100.0)
    position_y: float = Field(default=100.0)
    width: float = Field(default=280.0)
    height: float = Field(default=160.0)
    color_accent: Optional[str] = None
    metadata_json: Dict[str, Any] = Field(default_factory=dict)


class UpdateNodePositionPayload(BaseModel):
    position_x: Optional[float] = None
    position_y: Optional[float] = None
    status: Optional[str] = None
    confidence_score: Optional[float] = None


class AddCanvasEdgePayload(BaseModel):
    source_node_id: uuid.UUID
    target_node_id: uuid.UUID
    relation_type: str = Field(default="supports", pattern="^(supports|refutes|derives_from|correlates_with|branches_to|questions)$")
    label: Optional[str] = None
    weight: float = Field(default=1.0)
    metadata_json: Dict[str, Any] = Field(default_factory=dict)


class BrainstormCanvasPayload(BaseModel):
    topic: str = Field(..., min_length=3)


# ---------------- Route Implementations ----------------

@router.post("/boards", status_code=status.HTTP_201_CREATED)
async def create_canvas_board(
    payload: CreateCanvasBoardPayload,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Create a new research canvas board."""
    repo = CanvasRepository(session)
    board = DBCanvasBoard(
        user_id=current_user.id,
        workspace_id=payload.workspace_id,
        project_id=payload.project_id,
        research_job_id=payload.research_job_id,
        title=payload.title,
        description=payload.description,
        background_grid=payload.background_grid,
        status="active",
    )
    created = await repo.create_board(board)
    return {
        "id": str(created.id),
        "title": created.title,
        "description": created.description,
        "background_grid": created.background_grid,
        "viewport_state": created.viewport_state,
        "status": created.status,
        "created_at": created.created_at.isoformat(),
    }


@router.get("/metrics")
async def get_canvas_platform_metrics(
    workspace_id: Optional[uuid.UUID] = Query(None),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Query aggregate canvas boards, visual nodes, and relational edge metrics."""
    repo = CanvasRepository(session)
    return await repo.get_canvas_metrics(workspace_id=workspace_id)


@router.get("/boards")
async def list_canvas_boards(
    workspace_id: Optional[uuid.UUID] = Query(None),
    project_id: Optional[uuid.UUID] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> List[Dict[str, Any]]:
    """List research canvas boards."""
    repo = CanvasRepository(session)
    boards = await repo.list_boards(
        user_id=current_user.id if not workspace_id else None,
        workspace_id=workspace_id,
        project_id=project_id,
        limit=limit,
        offset=offset,
    )
    return [
        {
            "id": str(b.id),
            "title": b.title,
            "description": b.description,
            "background_grid": b.background_grid,
            "status": b.status,
            "created_at": b.created_at.isoformat(),
        }
        for b in boards
    ]


@router.get("/boards/{board_id}")
async def get_canvas_board(
    board_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Fetch complete research canvas board with all child visual nodes and relational edges."""
    repo = CanvasRepository(session)
    board = await repo.get_board(board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Canvas board not found")

    return {
        "id": str(board.id),
        "title": board.title,
        "description": board.description,
        "viewport_state": board.viewport_state,
        "background_grid": board.background_grid,
        "status": board.status,
        "created_at": board.created_at.isoformat(),
        "nodes": [
            {
                "id": str(n.id),
                "node_type": n.node_type,
                "title": n.title,
                "content": n.content,
                "confidence_score": n.confidence_score,
                "status": n.status,
                "position_x": n.position_x,
                "position_y": n.position_y,
                "width": n.width,
                "height": n.height,
                "color_accent": n.color_accent,
                "metadata_json": n.metadata_json,
                "created_at": n.created_at.isoformat(),
            }
            for n in board.nodes
        ],
        "edges": [
            {
                "id": str(e.id),
                "source_node_id": str(e.source_node_id),
                "target_node_id": str(e.target_node_id),
                "relation_type": e.relation_type,
                "label": e.label,
                "weight": e.weight,
                "metadata_json": e.metadata_json,
                "created_at": e.created_at.isoformat(),
            }
            for e in board.edges
        ],
    }


@router.post("/boards/{board_id}/generate", status_code=status.HTTP_201_CREATED)
async def generate_canvas_from_research(
    board_id: uuid.UUID,
    payload: GenerateCanvasFromResearchPayload,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Auto-generate structured 2D topological graph from research findings, evidence, and conclusions."""
    repo = CanvasRepository(session)
    board = await repo.get_board(board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Canvas board not found")

    generated = CanvasIdeationEngine.generate_canvas_from_research(
        title=payload.title,
        objective=payload.objective,
        findings=payload.findings,
        evidence=payload.evidence,
        conclusions=payload.conclusions,
    )

    db_nodes = [
        DBCanvasNode(
            id=uuid.UUID(n["id"]),
            canvas_id=board_id,
            node_type=n["node_type"],
            title=n["title"],
            content=n["content"],
            confidence_score=n["confidence_score"],
            status=n["status"],
            position_x=n["position_x"],
            position_y=n["position_y"],
            width=n["width"],
            height=n["height"],
            color_accent=n["color_accent"],
            metadata_json=n["metadata_json"],
        )
        for n in generated["nodes"]
    ]

    db_edges = [
        DBCanvasEdge(
            id=uuid.UUID(e["id"]),
            canvas_id=board_id,
            source_node_id=uuid.UUID(e["source_node_id"]),
            target_node_id=uuid.UUID(e["target_node_id"]),
            relation_type=e["relation_type"],
            label=e["label"],
            weight=e["weight"],
            metadata_json=e["metadata_json"],
        )
        for e in generated["edges"]
    ]

    result = await repo.batch_add_nodes_and_edges(board_id, db_nodes, db_edges)
    return {
        "board_id": str(board_id),
        "total_nodes_generated": result["nodes_added"],
        "total_edges_generated": result["edges_added"],
    }


@router.post("/boards/{board_id}/nodes", status_code=status.HTTP_201_CREATED)
async def add_canvas_node(
    board_id: uuid.UUID,
    payload: AddCanvasNodePayload,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Add a visual research node to the canvas."""
    repo = CanvasRepository(session)
    board = await repo.get_board(board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Canvas board not found")

    color = payload.color_accent or CanvasIdeationEngine.NODE_COLORS.get(payload.node_type, "#3b82f6")
    node = DBCanvasNode(
        canvas_id=board_id,
        node_type=payload.node_type,
        title=payload.title,
        content=payload.content,
        confidence_score=payload.confidence_score,
        status=payload.status,
        position_x=payload.position_x,
        position_y=payload.position_y,
        width=payload.width,
        height=payload.height,
        color_accent=color,
        metadata_json=payload.metadata_json,
    )
    created = await repo.add_node(node)
    return {
        "id": str(created.id),
        "canvas_id": str(created.canvas_id),
        "node_type": created.node_type,
        "title": created.title,
        "position_x": created.position_x,
        "position_y": created.position_y,
        "color_accent": created.color_accent,
    }


@router.patch("/boards/{board_id}/nodes/{node_id}")
async def update_canvas_node(
    board_id: uuid.UUID,
    node_id: uuid.UUID,
    payload: UpdateNodePositionPayload,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Update canvas node coordinates or status."""
    repo = CanvasRepository(session)
    updated = await repo.update_node(
        node_id=node_id,
        position_x=payload.position_x,
        position_y=payload.position_y,
        status=payload.status,
        confidence_score=payload.confidence_score,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Canvas node not found")

    return {
        "id": str(updated.id),
        "position_x": updated.position_x,
        "position_y": updated.position_y,
        "status": updated.status,
        "confidence_score": updated.confidence_score,
    }


@router.post("/boards/{board_id}/edges", status_code=status.HTTP_201_CREATED)
async def add_canvas_edge(
    board_id: uuid.UUID,
    payload: AddCanvasEdgePayload,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Add a relational connection link between two canvas nodes."""
    repo = CanvasRepository(session)
    board = await repo.get_board(board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Canvas board not found")

    edge = DBCanvasEdge(
        canvas_id=board_id,
        source_node_id=payload.source_node_id,
        target_node_id=payload.target_node_id,
        relation_type=payload.relation_type,
        label=payload.label,
        weight=payload.weight,
        metadata_json=payload.metadata_json,
    )
    created = await repo.add_edge(edge)
    return {
        "id": str(created.id),
        "canvas_id": str(created.canvas_id),
        "source_node_id": str(created.source_node_id),
        "target_node_id": str(created.target_node_id),
        "relation_type": created.relation_type,
        "label": created.label,
    }


@router.post("/boards/{board_id}/brainstorm", status_code=status.HTTP_201_CREATED)
async def brainstorm_canvas_nodes(
    board_id: uuid.UUID,
    payload: BrainstormCanvasPayload,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """AI Agent visual brainstorming: proposes counter-hypotheses and orthogonal inquiries."""
    repo = CanvasRepository(session)
    board = await repo.get_board(board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Canvas board not found")

    existing_nodes_dict = [
        {"id": str(n.id), "position_x": n.position_x, "position_y": n.position_y}
        for n in board.nodes
    ]

    brainstorm_res = CanvasIdeationEngine.synthesize_agent_brainstorm_nodes(
        topic=payload.topic,
        existing_nodes=existing_nodes_dict,
    )

    db_nodes = [
        DBCanvasNode(
            id=uuid.UUID(n["id"]),
            canvas_id=board_id,
            node_type=n["node_type"],
            title=n["title"],
            content=n["content"],
            confidence_score=n["confidence_score"],
            status=n["status"],
            position_x=n["position_x"],
            position_y=n["position_y"],
            width=n["width"],
            height=n["height"],
            color_accent=n["color_accent"],
            metadata_json=n["metadata_json"],
        )
        for n in brainstorm_res["brainstormed_nodes"]
    ]

    db_edges = [
        DBCanvasEdge(
            id=uuid.UUID(e["id"]),
            canvas_id=board_id,
            source_node_id=uuid.UUID(e["source_node_id"]),
            target_node_id=uuid.UUID(e["target_node_id"]),
            relation_type=e["relation_type"],
            label=e["label"],
            weight=e["weight"],
            metadata_json=e["metadata_json"],
        )
        for e in brainstorm_res["brainstormed_edges"]
    ]

    result = await repo.batch_add_nodes_and_edges(board_id, db_nodes, db_edges)
    return {
        "board_id": str(board_id),
        "brainstormed_nodes_count": result["nodes_added"],
        "brainstormed_edges_count": result["edges_added"],
    }


@router.delete("/boards/{board_id}", status_code=status.HTTP_200_OK)
async def delete_canvas_board(
    board_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Delete canvas board and all associated visual nodes and edges."""
    repo = CanvasRepository(session)
    deleted = await repo.delete_board(board_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Canvas board not found")
    return {"message": "Canvas board deleted", "id": str(board_id)}
