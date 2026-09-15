"""Super-Graph & Hypothesis Discovery REST API Routes (Phase 44)."""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db_session, get_current_user
from database.models.user import User as DBUser
from database.repositories.super_graph_repo import SuperGraphRepository
from research.super_graph_engine import SuperGraphHypothesisEngine

router = APIRouter(prefix="/supergraph", tags=["Scientific Super-Graph & Hypotheses"])

class SuperGraphNodeDTO(BaseModel):
    id: str
    canonical_id: str
    label: str
    entity_type: str
    degree_centrality: float
    pagerank_score: float

class SuperGraphEdgeDTO(BaseModel):
    id: str
    source_node_id: str
    target_node_id: str
    relation_type: str
    confidence_score: float
    is_predicted: bool

class CausalHypothesisDTO(BaseModel):
    id: str
    title: str
    premise_statement: str
    mechanistic_chain: Optional[List[str]] = None
    novelty_score: float
    biological_plausibility: float
    falsifiability_index: float
    recommended_experiment: Optional[str] = None
    status: str
    created_at: str

class GenerateHypothesisRequest(BaseModel):
    focus_entity: str = Field("PCSK9", description="Entity of interest for hypothesis synthesis")
    workspace_id: Optional[str] = None
    project_id: Optional[str] = None

@router.post("/init-seed", status_code=status.HTTP_201_CREATED)
async def init_supergraph_seed(
    db: AsyncSession = Depends(get_db_session),
    user: Optional[DBUser] = Depends(get_current_user),
):
    repo = SuperGraphRepository(db)
    engine = SuperGraphHypothesisEngine()
    seed = engine.generate_seed_supergraph()

    node_map = {}
    for n in seed["nodes"]:
        created = await repo.create_node(
            canonical_id=n["canonical_id"],
            label=n["label"],
            entity_type=n["type"],
            degree_centrality=n["degree"],
            pagerank_score=n["pagerank"],
        )
        node_map[n["canonical_id"]] = created.id

    for e in seed["edges"]:
        src_id = node_map.get(e["source"])
        tgt_id = node_map.get(e["target"])
        if src_id and tgt_id:
            await repo.create_edge(
                source_node_id=src_id,
                target_node_id=tgt_id,
                relation_type=e["relation"],
                confidence_score=e["confidence"],
                is_predicted=e["predicted"],
            )

    return {"status": "SUCCESS", "nodes_seeded": len(seed["nodes"]), "edges_seeded": len(seed["edges"])}

@router.get("/nodes", response_model=List[SuperGraphNodeDTO])
async def list_supergraph_nodes(
    entity_type: Optional[str] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db_session),
    user: Optional[DBUser] = Depends(get_current_user),
):
    repo = SuperGraphRepository(db)
    nodes = await repo.list_nodes(entity_type=entity_type, limit=limit)
    return [
        SuperGraphNodeDTO(
            id=str(n.id),
            canonical_id=n.canonical_id,
            label=n.label,
            entity_type=n.entity_type,
            degree_centrality=n.degree_centrality,
            pagerank_score=n.pagerank_score,
        )
        for n in nodes
    ]

@router.get("/edges", response_model=List[SuperGraphEdgeDTO])
async def list_supergraph_edges(
    relation_type: Optional[str] = None,
    is_predicted: Optional[bool] = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db_session),
    user: Optional[DBUser] = Depends(get_current_user),
):
    repo = SuperGraphRepository(db)
    edges = await repo.list_edges(relation_type=relation_type, is_predicted=is_predicted, limit=limit)
    return [
        SuperGraphEdgeDTO(
            id=str(e.id),
            source_node_id=str(e.source_node_id),
            target_node_id=str(e.target_node_id),
            relation_type=e.relation_type,
            confidence_score=e.confidence_score,
            is_predicted=e.is_predicted,
        )
        for e in edges
    ]

@router.post("/hypotheses/formulate", response_model=List[CausalHypothesisDTO], status_code=status.HTTP_201_CREATED)
async def formulate_hypotheses(
    req: GenerateHypothesisRequest,
    db: AsyncSession = Depends(get_db_session),
    user: Optional[DBUser] = Depends(get_current_user),
):
    repo = SuperGraphRepository(db)
    engine = SuperGraphHypothesisEngine()
    hypotheses = engine.formulate_causal_hypotheses(focus_entity=req.focus_entity)

    results = []
    for h in hypotheses:
        created = await repo.create_hypothesis(
            title=h["title"],
            premise_statement=h["premise_statement"],
            mechanistic_chain=h["mechanistic_chain"],
            novelty_score=h["novelty_score"],
            biological_plausibility=h["biological_plausibility"],
            falsifiability_index=h["falsifiability_index"],
            recommended_experiment=h["recommended_experiment"],
            workspace_id=req.workspace_id,
            project_id=req.project_id,
        )
        results.append(
            CausalHypothesisDTO(
                id=str(created.id),
                title=created.title,
                premise_statement=created.premise_statement,
                mechanistic_chain=created.mechanistic_chain,
                novelty_score=created.novelty_score,
                biological_plausibility=created.biological_plausibility,
                falsifiability_index=created.falsifiability_index,
                recommended_experiment=created.recommended_experiment,
                status=created.status,
                created_at=created.created_at.isoformat(),
            )
        )
    return results

@router.get("/hypotheses", response_model=List[CausalHypothesisDTO])
async def list_hypotheses(
    status: Optional[str] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db_session),
    user: Optional[DBUser] = Depends(get_current_user),
):
    repo = SuperGraphRepository(db)
    hypotheses = await repo.list_hypotheses(status=status, limit=limit)
    return [
        CausalHypothesisDTO(
            id=str(h.id),
            title=h.title,
            premise_statement=h.premise_statement,
            mechanistic_chain=h.mechanistic_chain,
            novelty_score=h.novelty_score,
            biological_plausibility=h.biological_plausibility,
            falsifiability_index=h.falsifiability_index,
            recommended_experiment=h.recommended_experiment,
            status=h.status,
            created_at=h.created_at.isoformat(),
        )
        for h in hypotheses
    ]
