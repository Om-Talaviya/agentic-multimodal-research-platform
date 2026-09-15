"""Repository for Knowledge Graph entities and relations."""

from collections import deque
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from uuid import UUID
from sqlalchemy import or_, select, func, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession
from database.models.graph import DBKnowledgeEntity, DBKnowledgeRelation
from shared.logging import get_logger

logger = get_logger(__name__)


class KnowledgeGraphRepository:
    """Async repository for managing graph entities, relations, and subgraph traversals."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # -------------------------------------------------------------------------
    # Entity Operations
    # -------------------------------------------------------------------------

    async def create_entity(
        self,
        name: str,
        canonical_name: Optional[str] = None,
        entity_type: str = "CONCEPT",
        user_id: Optional[UUID] = None,
        project_id: Optional[UUID] = None,
        description: Optional[str] = None,
        aliases: Optional[List[str]] = None,
        properties: Optional[Dict[str, Any]] = None,
        confidence: float = 1.0,
    ) -> DBKnowledgeEntity:
        """Create a new knowledge entity node."""
        canonical = canonical_name.strip().lower() if canonical_name else name.strip().lower()
        entity = DBKnowledgeEntity(
            name=name.strip(),
            canonical_name=canonical,
            entity_type=entity_type.upper(),
            user_id=user_id,
            project_id=project_id,
            description=description,
            aliases=aliases or [],
            properties_json=properties or {},
            confidence=confidence,
        )
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def get_entity_by_id(self, entity_id: Union[str, UUID]) -> Optional[DBKnowledgeEntity]:
        """Fetch entity by primary key."""
        uid = UUID(str(entity_id))
        stmt = select(DBKnowledgeEntity).where(DBKnowledgeEntity.id == uid)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def find_entity_by_name(
        self,
        name: str,
        user_id: Optional[UUID] = None,
    ) -> Optional[DBKnowledgeEntity]:
        """Find entity by exact name, canonical name, or aliases."""
        clean_name = name.strip()
        canonical = clean_name.lower()

        conditions = [
            DBKnowledgeEntity.name == clean_name,
            DBKnowledgeEntity.canonical_name == canonical,
        ]

        stmt = select(DBKnowledgeEntity).where(or_(*conditions))
        if user_id:
            stmt = stmt.where(
                or_(DBKnowledgeEntity.user_id == user_id, DBKnowledgeEntity.user_id.is_(None))
            )

        res = await self.session.execute(stmt)
        matched = res.scalars().all()
        if matched:
            return matched[0]

        # Check aliases in memory or fallback search
        all_stmt = select(DBKnowledgeEntity)
        if user_id:
            all_stmt = all_stmt.where(
                or_(DBKnowledgeEntity.user_id == user_id, DBKnowledgeEntity.user_id.is_(None))
            )
        all_res = await self.session.execute(all_stmt)
        for ent in all_res.scalars().all():
            if ent.aliases and any(
                alias.strip().lower() == canonical for alias in ent.aliases if isinstance(alias, str)
            ):
                return ent

        return None

    async def find_or_create_entity(
        self,
        name: str,
        entity_type: str = "CONCEPT",
        user_id: Optional[UUID] = None,
        project_id: Optional[UUID] = None,
        description: Optional[str] = None,
        aliases: Optional[List[str]] = None,
        properties: Optional[Dict[str, Any]] = None,
        confidence: float = 1.0,
    ) -> DBKnowledgeEntity:
        """Find existing entity by name/canonical name or create a new one."""
        existing = await self.find_entity_by_name(name, user_id=user_id)
        if existing:
            # Merge aliases if new ones provided
            if aliases:
                current_aliases = set(existing.aliases or [])
                current_aliases.update([a.strip() for a in aliases if a.strip()])
                existing.aliases = list(current_aliases)
            if description and not existing.description:
                existing.description = description
            if properties and existing.properties_json:
                existing.properties_json = {**existing.properties_json, **properties}
            await self.session.commit()
            await self.session.refresh(existing)
            return existing

        return await self.create_entity(
            name=name,
            entity_type=entity_type,
            user_id=user_id,
            project_id=project_id,
            description=description,
            aliases=aliases,
            properties=properties,
            confidence=confidence,
        )

    async def list_entities(
        self,
        user_id: Optional[UUID] = None,
        project_id: Optional[UUID] = None,
        entity_type: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[DBKnowledgeEntity]:
        """List entities with optional filtering and text search."""
        stmt = select(DBKnowledgeEntity)
        conditions = []

        if user_id:
            conditions.append(
                or_(DBKnowledgeEntity.user_id == user_id, DBKnowledgeEntity.user_id.is_(None))
            )
        if project_id:
            conditions.append(DBKnowledgeEntity.project_id == project_id)
        if entity_type and entity_type.upper() != "ALL":
            conditions.append(DBKnowledgeEntity.entity_type == entity_type.upper())
        if search:
            s = f"%{search.strip().lower()}%"
            conditions.append(
                or_(
                    DBKnowledgeEntity.name.ilike(s),
                    DBKnowledgeEntity.canonical_name.ilike(s),
                    DBKnowledgeEntity.description.ilike(s),
                )
            )

        if conditions:
            stmt = stmt.where(and_(*conditions))

        stmt = stmt.order_by(DBKnowledgeEntity.confidence.desc(), DBKnowledgeEntity.created_at.desc())
        stmt = stmt.limit(limit).offset(offset)

        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def count_entities(
        self,
        user_id: Optional[UUID] = None,
        entity_type: Optional[str] = None,
    ) -> int:
        """Count total entities for user/type."""
        stmt = select(func.count(DBKnowledgeEntity.id))
        conditions = []
        if user_id:
            conditions.append(
                or_(DBKnowledgeEntity.user_id == user_id, DBKnowledgeEntity.user_id.is_(None))
            )
        if entity_type and entity_type.upper() != "ALL":
            conditions.append(DBKnowledgeEntity.entity_type == entity_type.upper())
        if conditions:
            stmt = stmt.where(and_(*conditions))
        res = await self.session.execute(stmt)
        return res.scalar_one() or 0

    async def update_entity(
        self,
        entity_id: Union[str, UUID],
        name: Optional[str] = None,
        entity_type: Optional[str] = None,
        description: Optional[str] = None,
        aliases: Optional[List[str]] = None,
        properties: Optional[Dict[str, Any]] = None,
        confidence: Optional[float] = None,
    ) -> Optional[DBKnowledgeEntity]:
        """Update entity fields."""
        entity = await self.get_entity_by_id(entity_id)
        if not entity:
            return None

        if name:
            entity.name = name.strip()
            entity.canonical_name = name.strip().lower()
        if entity_type:
            entity.entity_type = entity_type.upper()
        if description is not None:
            entity.description = description
        if aliases is not None:
            entity.aliases = aliases
        if properties is not None:
            entity.properties_json = properties
        if confidence is not None:
            entity.confidence = confidence

        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def delete_entity(self, entity_id: Union[str, UUID]) -> bool:
        """Delete an entity and cascade all its relation edges."""
        entity = await self.get_entity_by_id(entity_id)
        if not entity:
            return False
        await self.session.delete(entity)
        await self.session.commit()
        return True

    # -------------------------------------------------------------------------
    # Relation / Edge Operations
    # -------------------------------------------------------------------------

    async def create_relation(
        self,
        source_id: Union[str, UUID],
        target_id: Union[str, UUID],
        relation_type: str = "RELATES_TO",
        user_id: Optional[UUID] = None,
        project_id: Optional[UUID] = None,
        job_id: Optional[UUID] = None,
        description: Optional[str] = None,
        weight: float = 1.0,
        confidence: float = 1.0,
        evidence_id: Optional[UUID] = None,
        properties: Optional[Dict[str, Any]] = None,
    ) -> DBKnowledgeRelation:
        """Create a directed relation between two entities."""
        src_uid = UUID(str(source_id))
        tgt_uid = UUID(str(target_id))

        relation = DBKnowledgeRelation(
            source_id=src_uid,
            target_id=tgt_uid,
            relation_type=relation_type.upper(),
            user_id=user_id,
            project_id=project_id,
            job_id=job_id,
            description=description,
            weight=weight,
            confidence=confidence,
            evidence_id=evidence_id,
            properties_json=properties or {},
        )
        self.session.add(relation)
        await self.session.commit()
        await self.session.refresh(relation)
        return relation

    async def get_relation_by_id(self, relation_id: Union[str, UUID]) -> Optional[DBKnowledgeRelation]:
        """Fetch relation by primary key."""
        uid = UUID(str(relation_id))
        stmt = select(DBKnowledgeRelation).where(DBKnowledgeRelation.id == uid)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_relations(
        self,
        user_id: Optional[UUID] = None,
        entity_id: Optional[Union[str, UUID]] = None,
        source_id: Optional[Union[str, UUID]] = None,
        target_id: Optional[Union[str, UUID]] = None,
        relation_type: Optional[str] = None,
        job_id: Optional[UUID] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[DBKnowledgeRelation]:
        """List relation edges with optional entity, source, target, or type filtering."""
        stmt = select(DBKnowledgeRelation)
        conditions = []

        if user_id:
            conditions.append(
                or_(DBKnowledgeRelation.user_id == user_id, DBKnowledgeRelation.user_id.is_(None))
            )
        if entity_id:
            e_uid = UUID(str(entity_id))
            conditions.append(
                or_(
                    DBKnowledgeRelation.source_id == e_uid,
                    DBKnowledgeRelation.target_id == e_uid,
                )
            )
        if source_id:
            s_uid = UUID(str(source_id))
            conditions.append(DBKnowledgeRelation.source_id == s_uid)
        if target_id:
            t_uid = UUID(str(target_id))
            conditions.append(DBKnowledgeRelation.target_id == t_uid)
        if relation_type and relation_type.upper() != "ALL":
            conditions.append(DBKnowledgeRelation.relation_type == relation_type.upper())
        if job_id:
            conditions.append(DBKnowledgeRelation.job_id == job_id)

        if conditions:
            stmt = stmt.where(and_(*conditions))

        stmt = stmt.order_by(DBKnowledgeRelation.weight.desc(), DBKnowledgeRelation.created_at.desc())
        stmt = stmt.limit(limit).offset(offset)

        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def delete_relation(self, relation_id: Union[str, UUID]) -> bool:
        """Delete a relation edge."""
        relation = await self.get_relation_by_id(relation_id)
        if not relation:
            return False
        await self.session.delete(relation)
        await self.session.commit()
        return True

    # -------------------------------------------------------------------------
    # Graph Traversal & Subgraph Queries
    # -------------------------------------------------------------------------

    async def get_k_hop_subgraph(
        self,
        entity_id: Union[str, UUID],
        max_hops: int = 2,
        k_hops: Optional[int] = None,
        limit_nodes: int = 50,
        limit_edges: int = 100,
    ) -> Dict[str, Any]:
        """Extract a k-hop subgraph centered around a target entity node using BFS."""
        effective_hops = k_hops if k_hops is not None else max_hops
        root_uid = UUID(str(entity_id))
        root_entity = await self.get_entity_by_id(root_uid)
        if not root_entity:
            return {"nodes": [], "edges": []}

        visited_nodes: Set[UUID] = {root_uid}
        collected_entities: Dict[UUID, DBKnowledgeEntity] = {root_uid: root_entity}
        collected_relations: Dict[UUID, DBKnowledgeRelation] = {}

        queue: deque[Tuple[UUID, int]] = deque([(root_uid, 0)])

        while queue and len(collected_entities) < limit_nodes:
            current_id, depth = queue.popleft()
            if depth >= effective_hops:
                continue

            # Find all outgoing and incoming relations for current node
            stmt = select(DBKnowledgeRelation).where(
                or_(
                    DBKnowledgeRelation.source_id == current_id,
                    DBKnowledgeRelation.target_id == current_id,
                )
            )
            res = await self.session.execute(stmt)
            relations = res.scalars().all()

            for rel in relations:
                if len(collected_relations) >= limit_edges:
                    break
                collected_relations[rel.id] = rel

                neighbor_id = rel.target_id if rel.source_id == current_id else rel.source_id
                if neighbor_id not in visited_nodes and len(collected_entities) < limit_nodes:
                    visited_nodes.add(neighbor_id)
                    neighbor_entity = await self.get_entity_by_id(neighbor_id)
                    if neighbor_entity:
                        collected_entities[neighbor_id] = neighbor_entity
                        queue.append((neighbor_id, depth + 1))

        nodes_data = [e.to_dict() for e in collected_entities.values()]
        edges_data = [r.to_dict() for r in collected_relations.values()]

        return {"nodes": nodes_data, "edges": edges_data}

    async def find_shortest_path(
        self,
        source_id: Union[str, UUID],
        target_id: Union[str, UUID],
        max_depth: int = 4,
    ) -> Optional[List[Dict[str, Any]]]:
        """Find the shortest path of entity nodes and relation edges between source and target."""
        src_uid = UUID(str(source_id))
        tgt_uid = UUID(str(target_id))

        if src_uid == tgt_uid:
            src = await self.get_entity_by_id(src_uid)
            return [{"node": src.to_dict()}] if src else None

        # BFS for shortest path: queue stores (current_id, path_tuples)
        # path_tuple: list of (node_id, edge_id, direction)
        queue: deque[Tuple[UUID, List[Dict[str, Any]]]] = deque([(src_uid, [])])
        visited: Set[UUID] = {src_uid}

        while queue:
            current_id, path = queue.popleft()
            if len(path) >= max_depth:
                continue

            stmt = select(DBKnowledgeRelation).where(
                or_(
                    DBKnowledgeRelation.source_id == current_id,
                    DBKnowledgeRelation.target_id == current_id,
                )
            )
            res = await self.session.execute(stmt)
            relations = res.scalars().all()

            for rel in relations:
                is_outgoing = rel.source_id == current_id
                next_id = rel.target_id if is_outgoing else rel.source_id

                new_step = {
                    "from_id": str(current_id),
                    "to_id": str(next_id),
                    "relation_id": str(rel.id),
                    "relation_type": rel.relation_type,
                    "description": rel.description,
                    "direction": "OUTGOING" if is_outgoing else "INCOMING",
                }
                new_path = path + [new_step]

                if next_id == tgt_uid:
                    # Resolve full node details for the path
                    return new_path

                if next_id not in visited:
                    visited.add(next_id)
                    queue.append((next_id, new_path))

        return None

    # -------------------------------------------------------------------------
    # Batch Triplet Ingestion
    # -------------------------------------------------------------------------

    async def batch_upsert_triplets(
        self,
        triplets: List[Dict[str, Any]],
        user_id: Optional[UUID] = None,
        job_id: Optional[UUID] = None,
        project_id: Optional[UUID] = None,
    ) -> Tuple[List[DBKnowledgeEntity], List[DBKnowledgeRelation]]:
        """Batch upsert entities and relation triplets:
        Each triplet item format:
        {
            "source": "Polylactic Acid",
            "source_type": "MATERIAL",
            "relation": "DEGRADES_IN",
            "target": "Seawater",
            "target_type": "ENVIRONMENT",
            "description": "Degrades at <1.5%/yr in ambient seawater",
            "confidence": 0.95,
            "weight": 1.0
        }
        """
        created_entities: Dict[str, DBKnowledgeEntity] = {}
        created_relations: List[DBKnowledgeRelation] = []

        for item in triplets:
            src_name = item.get("source", "").strip()
            tgt_name = item.get("target", "").strip()
            rel_type = item.get("relation", "RELATES_TO").strip().upper()
            if not src_name or not tgt_name:
                continue

            src_type = item.get("source_type", "CONCEPT")
            tgt_type = item.get("target_type", "CONCEPT")

            src_entity = await self.find_or_create_entity(
                name=src_name,
                entity_type=src_type,
                user_id=user_id,
                project_id=project_id,
            )
            created_entities[src_entity.canonical_name] = src_entity

            tgt_entity = await self.find_or_create_entity(
                name=tgt_name,
                entity_type=tgt_type,
                user_id=user_id,
                project_id=project_id,
            )
            created_entities[tgt_entity.canonical_name] = tgt_entity

            # Check if relation already exists between these two entities
            existing_rel_stmt = select(DBKnowledgeRelation).where(
                and_(
                    DBKnowledgeRelation.source_id == src_entity.id,
                    DBKnowledgeRelation.target_id == tgt_entity.id,
                    DBKnowledgeRelation.relation_type == rel_type,
                )
            )
            rel_res = await self.session.execute(existing_rel_stmt)
            existing_rel = rel_res.scalar_one_or_none()

            desc = item.get("description")
            conf = float(item.get("confidence", 1.0))
            weight = float(item.get("weight", 1.0))

            if existing_rel:
                if desc and not existing_rel.description:
                    existing_rel.description = desc
                existing_rel.weight = max(existing_rel.weight, weight)
                existing_rel.confidence = max(existing_rel.confidence, conf)
                created_relations.append(existing_rel)
            else:
                rel = await self.create_relation(
                    source_id=src_entity.id,
                    target_id=tgt_entity.id,
                    relation_type=rel_type,
                    user_id=user_id,
                    project_id=project_id,
                    job_id=job_id,
                    description=desc,
                    weight=weight,
                    confidence=conf,
                )
                created_relations.append(rel)

        await self.session.commit()
        return list(created_entities.values()), created_relations
