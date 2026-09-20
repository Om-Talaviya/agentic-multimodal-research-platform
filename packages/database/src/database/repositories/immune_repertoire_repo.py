"""
Repository for Phase 104: Immune Repertoire & TCR/BCR Clonotypes.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
import uuid

from database.models.immune_repertoire import DBImmuneRepertoire, DBTCRClonotype, DBVDJRecombination

class ImmuneRepertoireRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_repertoire(
        self,
        sample_name: str,
        user_id: Optional[uuid.UUID] = None,
        organism: str = "Homo sapiens",
        chain_type: str = "TCR_ALPHA_BETA",
        total_cells: int = 0,
        shannon_entropy: float = 0.0,
        gini_simpson_index: float = 0.0,
        clonality_score: float = 0.0,
        metadata_json: Optional[Dict[str, Any]] = None,
    ) -> DBImmuneRepertoire:
        repertoire = DBImmuneRepertoire(
            id=uuid.uuid4(),
            user_id=user_id,
            sample_name=sample_name,
            organism=organism,
            chain_type=chain_type,
            total_cells=total_cells,
            shannon_entropy=shannon_entropy,
            gini_simpson_index=gini_simpson_index,
            clonality_score=clonality_score,
            metadata_json=metadata_json or {},
            status="COMPLETED"
        )
        self.session.add(repertoire)
        await self.session.commit()
        await self.session.refresh(repertoire)
        return repertoire

    async def get_repertoire(self, repertoire_id: uuid.UUID) -> Optional[DBImmuneRepertoire]:
        stmt = (
            select(DBImmuneRepertoire)
            .options(selectinload(DBImmuneRepertoire.clonotypes), selectinload(DBImmuneRepertoire.vdj_pairings))
            .where(DBImmuneRepertoire.id == repertoire_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_repertoires(self, limit: int = 50, offset: int = 0) -> List[DBImmuneRepertoire]:
        stmt = (
            select(DBImmuneRepertoire)
            .order_by(desc(DBImmuneRepertoire.created_at))
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_clonotypes(
        self,
        repertoire_id: uuid.UUID,
        clonotypes_data: List[Dict[str, Any]]
    ) -> List[DBTCRClonotype]:
        entities = []
        for c in clonotypes_data:
            entity = DBTCRClonotype(
                id=uuid.uuid4(),
                repertoire_id=repertoire_id,
                cdr3_nt=c.get("cdr3_nt"),
                cdr3_aa=c["cdr3_aa"],
                v_gene=c["v_gene"],
                d_gene=c.get("d_gene"),
                j_gene=c["j_gene"],
                c_gene=c.get("c_gene"),
                frequency=c.get("frequency", 0.0),
                count=c.get("count", 1),
                is_productive=c.get("is_productive", True),
                antigen_specificity=c.get("antigen_specificity")
            )
            entities.append(entity)
            self.session.add(entity)

        # Update repertoire count
        repertoire = await self.session.get(DBImmuneRepertoire, repertoire_id)
        if repertoire:
            repertoire.clonotype_count = len(entities)

        await self.session.commit()
        return entities

    async def add_vdj_pairings(
        self,
        repertoire_id: uuid.UUID,
        pairings_data: List[Dict[str, Any]]
    ) -> List[DBVDJRecombination]:
        entities = []
        for p in pairings_data:
            entity = DBVDJRecombination(
                id=uuid.uuid4(),
                repertoire_id=repertoire_id,
                v_family=p["v_family"],
                j_family=p["j_family"],
                pairing_frequency=p.get("pairing_frequency", 0.0),
                cdr3_length=p.get("cdr3_length", 15)
            )
            entities.append(entity)
            self.session.add(entity)
        await self.session.commit()
        return entities
