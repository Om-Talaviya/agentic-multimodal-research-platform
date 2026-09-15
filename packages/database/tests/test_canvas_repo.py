import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from database.connection import Base
from database.models.canvas import DBCanvasBoard, DBCanvasEdge, DBCanvasNode
from database.repositories.canvas_repo import CanvasRepository


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
async def test_canvas_repo_full_lifecycle(db_session: AsyncSession):
    """Test full Canvas board, node, edge, and metrics lifecycle."""
    repo = CanvasRepository(db_session)
    user_id = uuid.uuid4()

    # 1. Create Board
    board = DBCanvasBoard(
        user_id=user_id,
        title="Quantum Advantage DAG",
        description="Exploratory visual DAG for Hamiltonian solvers.",
        viewport_state={"zoom": 1.0, "pan_x": 0.0, "pan_y": 0.0},
        background_grid="dots",
    )
    created_board = await repo.create_board(board)
    assert created_board.id is not None
    assert created_board.title == "Quantum Advantage DAG"
    assert created_board.status == "active"

    # 2. Get Board
    fetched_board = await repo.get_board(created_board.id)
    assert fetched_board is not None
    assert fetched_board.id == created_board.id
    assert len(fetched_board.nodes) == 0

    # 3. Add Nodes
    node1 = DBCanvasNode(
        canvas_id=created_board.id,
        node_type="hypothesis",
        title="Hypothesis: Super-polynomial speedup",
        content="Testing QAOA with depth-4 Hamiltonian",
        confidence_score=0.91,
        status="verified",
        position_x=100.0,
        position_y=200.0,
        width=260.0,
        height=140.0,
        color_accent="#3b82f6",
    )
    created_node1 = await repo.add_node(node1)
    assert created_node1.id is not None

    node2 = DBCanvasNode(
        canvas_id=created_board.id,
        node_type="evidence",
        title="Evidence: 128 Qubit Hardware",
        content="Experiment ran with 98.4% fidelity",
        confidence_score=0.96,
        status="verified",
        position_x=450.0,
        position_y=200.0,
        width=260.0,
        height=140.0,
        color_accent="#10b981",
    )
    created_node2 = await repo.add_node(node2)
    assert created_node2.id is not None

    # 4. Add Edge
    edge = DBCanvasEdge(
        canvas_id=created_board.id,
        source_node_id=created_node1.id,
        target_node_id=created_node2.id,
        relation_type="supports",
        label="empirically validates",
        weight=0.95,
    )
    created_edge = await repo.add_edge(edge)
    assert created_edge.id is not None
    assert created_edge.relation_type == "supports"

    # 5. List Boards
    boards = await repo.list_boards(user_id=user_id)
    assert len(boards) == 1
    assert boards[0].id == created_board.id

    # 6. Get Board with relationships loaded
    full_board = await repo.get_board(created_board.id)
    assert len(full_board.nodes) == 2
    assert len(full_board.edges) == 1

    # 7. Update Node Position
    updated_node = await repo.update_node(
        created_node1.id,
        position_x=120.0,
        position_y=220.0,
        confidence_score=0.94,
    )
    assert updated_node is not None
    assert updated_node.position_x == 120.0
    assert updated_node.confidence_score == 0.94

    # 8. Metrics
    metrics = await repo.get_canvas_metrics()
    assert metrics["total_canvas_boards"] == 1
    assert metrics["total_canvas_nodes"] == 2
    assert metrics["total_canvas_edges"] == 1
    assert metrics["node_type_distribution"].get("hypothesis") == 1
    assert metrics["node_type_distribution"].get("evidence") == 1

    # 9. Delete Board
    assert await repo.delete_board(created_board.id) is True
    assert await repo.get_board(created_board.id) is None
