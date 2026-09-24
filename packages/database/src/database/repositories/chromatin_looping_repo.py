"""Repository for Hi-C Chromatin Loop (Phase 152)."""

import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.chromatin_looping import (
    DBHiCChromatinLoopStudy,
    DBEnhancerPromoterContactEdge,
    DBTADBoundaryRegion,
)


class ChromatinLoopRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_study(
        self,
        cell_line_name: str,
        chromosome: str,
        genomic_resolution_bp: int,
        total_loops_detected: int,
        tad_count: int,
        mean_insulation_score: float,
        mean_loop_span_kb: float,
    ) -> DBHiCChromatinLoopStudy:
        study = DBHiCChromatinLoopStudy(
            id=uuid.uuid4(),
            cell_line_name=cell_line_name,
            chromosome=chromosome,
            genomic_resolution_bp=genomic_resolution_bp,
            total_loops_detected=total_loops_detected,
            tad_count=tad_count,
            mean_insulation_score=mean_insulation_score,
            mean_loop_span_kb=mean_loop_span_kb,
        )
        self.db.add(study)
        await self.db.commit()
        await self.db.refresh(study)
        return study

    async def add_contact_edge(
        self,
        study_id: uuid.UUID,
        enhancer_locus: str,
        target_gene: str,
        contact_frequency: float,
        loop_span_bp: int,
        ctcf_convergent_motif: bool,
        activation_log2fc: float,
    ) -> DBEnhancerPromoterContactEdge:
        rec = DBEnhancerPromoterContactEdge(
            id=uuid.uuid4(),
            study_id=study_id,
            enhancer_locus=enhancer_locus,
            target_gene=target_gene,
            contact_frequency=contact_frequency,
            loop_span_bp=loop_span_bp,
            ctcf_convergent_motif=ctcf_convergent_motif,
            activation_log2fc=activation_log2fc,
        )
        self.db.add(rec)
        await self.db.commit()
        await self.db.refresh(rec)
        return rec

    async def add_tad_boundary(
        self,
        study_id: uuid.UUID,
        start_bp: int,
        end_bp: int,
        insulation_score: float,
        ctcf_occupancy_score: float,
    ) -> DBTADBoundaryRegion:
        rec = DBTADBoundaryRegion(
            id=uuid.uuid4(),
            study_id=study_id,
            start_bp=start_bp,
            end_bp=end_bp,
            insulation_score=insulation_score,
            ctcf_occupancy_score=ctcf_occupancy_score,
        )
        self.db.add(rec)
        await self.db.commit()
        await self.db.refresh(rec)
        return rec

    async def get_study_with_details(self, study_id: uuid.UUID) -> Optional[DBHiCChromatinLoopStudy]:
        stmt = (
            select(DBHiCChromatinLoopStudy)
            .where(DBHiCChromatinLoopStudy.id == study_id)
            .options(
                selectinload(DBHiCChromatinLoopStudy.contact_edges),
                selectinload(DBHiCChromatinLoopStudy.tad_boundaries),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
