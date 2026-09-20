"""
Repository for Phase 107: Allosteric Pocket Discovery & Cryptic Binding Sites.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
import uuid

from database.models.cryptic_pockets import DBCrypticPocketAnalysis, DBAllostericPocketProfile, DBCoupledResidueNetwork

class CrypticPocketRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_analysis(
        self,
        target_protein: str,
        user_id: Optional[uuid.UUID] = None,
        pdb_id: Optional[str] = None,
        trajectory_frames_sampled: int = 100,
        max_druggability_score: float = 0.0,
        allosteric_coupling_score: float = 0.0,
        metadata_json: Optional[Dict[str, Any]] = None,
    ) -> DBCrypticPocketAnalysis:
        analysis = DBCrypticPocketAnalysis(
            id=uuid.uuid4(),
            user_id=user_id,
            target_protein=target_protein,
            pdb_id=pdb_id,
            trajectory_frames_sampled=trajectory_frames_sampled,
            max_druggability_score=max_druggability_score,
            allosteric_coupling_score=allosteric_coupling_score,
            metadata_json=metadata_json or {},
            status="COMPLETED"
        )
        self.session.add(analysis)
        await self.session.commit()
        await self.session.refresh(analysis)
        return analysis

    async def get_analysis(self, analysis_id: uuid.UUID) -> Optional[DBCrypticPocketAnalysis]:
        stmt = (
            select(DBCrypticPocketAnalysis)
            .options(selectinload(DBCrypticPocketAnalysis.pockets), selectinload(DBCrypticPocketAnalysis.coupled_networks))
            .where(DBCrypticPocketAnalysis.id == analysis_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_analyses(self, limit: int = 50, offset: int = 0) -> List[DBCrypticPocketAnalysis]:
        stmt = (
            select(DBCrypticPocketAnalysis)
            .order_by(desc(DBCrypticPocketAnalysis.created_at))
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_pockets(
        self,
        analysis_id: uuid.UUID,
        pockets_data: List[Dict[str, Any]]
    ) -> List[DBAllostericPocketProfile]:
        entities = []
        for p in pockets_data:
            entity = DBAllostericPocketProfile(
                id=uuid.uuid4(),
                analysis_id=analysis_id,
                pocket_name=p["pocket_name"],
                center_x=p.get("center_x", 0.0),
                center_y=p.get("center_y", 0.0),
                center_z=p.get("center_z", 0.0),
                apo_volume_a3=p.get("apo_volume_a3", 0.0),
                holo_volume_a3=p.get("holo_volume_a3", 0.0),
                volume_expansion_ratio=p.get("volume_expansion_ratio", 1.0),
                druggability_index=p.get("druggability_index", 0.0),
                hydrophobicity_score=p.get("hydrophobicity_score", 0.0),
                enclosing_residues=p.get("enclosing_residues")
            )
            entities.append(entity)
            self.session.add(entity)

        analysis = await self.session.get(DBCrypticPocketAnalysis, analysis_id)
        if analysis:
            analysis.detected_cryptic_pockets = len(entities)

        await self.session.commit()
        return entities

    async def add_coupled_networks(
        self,
        analysis_id: uuid.UUID,
        networks_data: List[Dict[str, Any]]
    ) -> List[DBCoupledResidueNetwork]:
        entities = []
        for net in networks_data:
            entity = DBCoupledResidueNetwork(
                id=uuid.uuid4(),
                analysis_id=analysis_id,
                source_residue=net["source_residue"],
                target_residue=net["target_residue"],
                allosteric_correlation=net.get("allosteric_correlation", 0.0),
                pathway_shortest_distance_a=net.get("pathway_shortest_distance_a", 0.0)
            )
            entities.append(entity)
            self.session.add(entity)
        await self.session.commit()
        return entities
