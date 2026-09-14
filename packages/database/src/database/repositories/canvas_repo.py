"""Repository for Research Canvas Boards, Nodes, and Relational Edges."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import delete, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.canvas import DBCanvasBoard, DBCanvasEdge, DBCanvasNode
from shared.logging import get_logger

logger = get_logger(__name__)


class CanvasRepository:
    """Async database repository for infinite research canvas and visual node-graph state."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_board(self, board: DBCanvasBoard) -> DBCanvasBoard:
        """Create a new research canvas board."""
        self.session.add(board)
        await self.session.commit()
        await self.session.refresh(board)
        logger.info("Created canvas board", board_id=str(board.id), title=board.title)
        return board

    async def get_board(self, board_id: uuid.UUID) -> Optional[DBCanvasBoard]:
        """Fetch canvas board with all child visual nodes and relational edges."""
        stmt = (
            select(DBCanvasBoard)
            .options(
                selectinload(DBCanvasBoard.nodes),
                selectinload(DBCanvasBoard.edges),
            )
            .execution_options(populate_existing=True)
            .where(DBCanvasBoard.id == board_id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_boards(
        self,
        user_id: Optional[uuid.UUID] = None,
        workspace_id: Optional[uuid.UUID] = None,
        project_id: Optional[uuid.UUID] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[DBCanvasBoard]:
        """List canvas boards with optional workspace and project filtering."""
        stmt = select(DBCanvasBoard).order_by(desc(DBCanvasBoard.created_at))

        if user_id:
            stmt = stmt.where(DBCanvasBoard.user_id == user_id)
        if workspace_id:
            stmt = stmt.where(DBCanvasBoard.workspace_id == workspace_id)
        if project_id:
            stmt = stmt.where(DBCanvasBoard.project_id == project_id)

        stmt = stmt.limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_board_viewport(
        self,
        board_id: uuid.UUID,
        viewport_state: Dict[str, Any],
    ) -> Optional[DBCanvasBoard]:
        """Update canvas zoom and pan coordinates."""
        board = await self.get_board(board_id)
        if not board:
            return None

        board.viewport_state = viewport_state
        board.updated_at = datetime.now(timezone.utc)
        await self.session.commit()
        await self.session.refresh(board)
        return board

    async def add_node(self, node: DBCanvasNode) -> DBCanvasNode:
        """Add a single visual node to the canvas."""
        self.session.add(node)
        await self.session.commit()
        await self.session.refresh(node)
        return node

    async def update_node(
        self,
        node_id: uuid.UUID,
        position_x: Optional[float] = None,
        position_y: Optional[float] = None,
        status: Optional[str] = None,
        confidence_score: Optional[float] = None,
    ) -> Optional[DBCanvasNode]:
        """Update node coordinates, verification status, or confidence score."""
        stmt = select(DBCanvasNode).where(DBCanvasNode.id == node_id)
        result = await self.session.execute(stmt)
        node = result.scalars().first()
        if not node:
            return None

        if position_x is not None:
            node.position_x = position_x
        if position_y is not None:
            node.position_y = position_y
        if status is not None:
            node.status = status
        if confidence_score is not None:
            node.confidence_score = confidence_score

        node.updated_at = datetime.now(timezone.utc)
        await self.session.commit()
        await self.session.refresh(node)
        return node

    async def add_edge(self, edge: DBCanvasEdge) -> DBCanvasEdge:
        """Add a directed relational edge connecting two nodes."""
        self.session.add(edge)
        await self.session.commit()
        await self.session.refresh(edge)
        return edge

    async def batch_add_nodes_and_edges(
        self,
        board_id: uuid.UUID,
        nodes: List[DBCanvasNode],
        edges: List[DBCanvasEdge],
    ) -> Dict[str, Any]:
        """Batch persist nodes and relational edges to a canvas board."""
        for n in nodes:
            n.canvas_id = board_id
            self.session.add(n)

        for e in edges:
            e.canvas_id = board_id
            self.session.add(e)

        await self.session.commit()
        return {
            "canvas_id": str(board_id),
            "nodes_added": len(nodes),
            "edges_added": len(edges),
        }

    async def delete_board(self, board_id: uuid.UUID) -> bool:
        """Delete canvas board and all associated nodes and edges."""
        stmt = delete(DBCanvasBoard).where(DBCanvasBoard.id == board_id)
        res = await self.session.execute(stmt)
        await self.session.commit()
        return (res.rowcount or 0) > 0

    async def get_canvas_metrics(
        self,
        workspace_id: Optional[uuid.UUID] = None,
    ) -> Dict[str, Any]:
        """Query platform-wide research canvas and node KPIs."""
        board_stmt = select(func.count(DBCanvasBoard.id))
        node_stmt = select(func.count(DBCanvasNode.id))
        edge_stmt = select(func.count(DBCanvasEdge.id))

        if workspace_id:
            board_stmt = board_stmt.where(DBCanvasBoard.workspace_id == workspace_id)

        total_boards = (await self.session.execute(board_stmt)).scalar() or 0
        total_nodes = (await self.session.execute(node_stmt)).scalar() or 0
        total_edges = (await self.session.execute(edge_stmt)).scalar() or 0

        # Node type breakdown
        type_stmt = select(DBCanvasNode.node_type, func.count(DBCanvasNode.id)).group_by(DBCanvasNode.node_type)
        type_rows = (await self.session.execute(type_stmt)).all()
        type_dist = {row[0]: row[1] for row in type_rows}

        return {
            "total_canvas_boards": total_boards,
            "total_canvas_nodes": total_nodes,
            "total_canvas_edges": total_edges,
            "node_type_distribution": type_dist,
            "average_nodes_per_board": round(total_nodes / max(1, total_boards), 1),
        }
