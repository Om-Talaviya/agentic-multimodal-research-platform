"""Super-Graph & Hypothesis Discovery Repository (Phase 44)."""
from typing import List, Optional, Dict, Any
from sqlalchemy import select, delete, desc
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.super_graph import (
    DBSuperGraphNode,
    DBSuperGraphEdge,
    DBCausalHypothesis,
)

class SuperGraphRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_node(
        self,
        canonical_id: str,
        label: str,
        entity_type: str,
        degree_centrality: float = 0.0,
        pagerank_score: float = 0.0,
        workspace_id: Optional[str] = None,
        project_id: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
    ) -> DBSuperGraphNode:
        node = DBSuperGraphNode(
            canonical_id=canonical_id,
            label=label,
            entity_type=entity_type,
            degree_centrality=degree_centrality,
            pagerank_score=pagerank_score,
            workspace_id=workspace_id,
            project_id=project_id,
            properties=properties or {},
        )
        self.session.add(node)
        await self.session.commit()
        await self.session.refresh(node)
        return node

    async def get_node(self, node_id: str) -> Optional[DBSuperGraphNode]:
        stmt = select(DBSuperGraphNode).where(DBSuperGraphNode.id == node_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_nodes(
        self,
        entity_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[DBSuperGraphNode]:
        stmt = select(DBSuperGraphNode)
        if entity_type:
            stmt = stmt.where(DBSuperGraphNode.entity_type.ilike(f"%{entity_type}%"))
        stmt = stmt.order_by(desc(DBSuperGraphNode.pagerank_score)).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create_edge(
        self,
        source_node_id: str,
        target_node_id: str,
        relation_type: str,
        confidence_score: float = 0.85,
        is_predicted: bool = False,
        meta_info: Optional[Dict[str, Any]] = None,
    ) -> DBSuperGraphEdge:
        edge = DBSuperGraphEdge(
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            relation_type=relation_type,
            confidence_score=confidence_score,
            is_predicted=is_predicted,
            meta_info=meta_info or {},
        )
        self.session.add(edge)
        await self.session.commit()
        await self.session.refresh(edge)
        return edge

    async def list_edges(
        self,
        relation_type: Optional[str] = None,
        is_predicted: Optional[bool] = None,
        limit: int = 100,
    ) -> List[DBSuperGraphEdge]:
        stmt = select(DBSuperGraphEdge)
        if relation_type:
            stmt = stmt.where(DBSuperGraphEdge.relation_type == relation_type)
        if is_predicted is not None:
            stmt = stmt.where(DBSuperGraphEdge.is_predicted == is_predicted)
        stmt = stmt.limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create_hypothesis(
        self,
        title: str,
        premise_statement: str,
        mechanistic_chain: List[str],
        novelty_score: float = 0.88,
        biological_plausibility: float = 0.92,
        falsifiability_index: float = 0.85,
        recommended_experiment: Optional[str] = None,
        workspace_id: Optional[str] = None,
        project_id: Optional[str] = None,
        meta_info: Optional[Dict[str, Any]] = None,
    ) -> DBCausalHypothesis:
        hypo = DBCausalHypothesis(
            title=title,
            premise_statement=premise_statement,
            mechanistic_chain=mechanistic_chain,
            novelty_score=novelty_score,
            biological_plausibility=biological_plausibility,
            falsifiability_index=falsifiability_index,
            recommended_experiment=recommended_experiment,
            workspace_id=workspace_id,
            project_id=project_id,
            meta_info=meta_info or {},
        )
        self.session.add(hypo)
        await self.session.commit()
        await self.session.refresh(hypo)
        return hypo

    async def list_hypotheses(
        self,
        status: Optional[str] = None,
        limit: int = 50,
    ) -> List[DBCausalHypothesis]:
        stmt = select(DBCausalHypothesis)
        if status:
            stmt = stmt.where(DBCausalHypothesis.status == status)
        stmt = stmt.order_by(desc(DBCausalHypothesis.novelty_score)).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
