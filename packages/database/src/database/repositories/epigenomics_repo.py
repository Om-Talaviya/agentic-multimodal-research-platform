"""
Repository for Autonomous Epigenomic Chromatin Accessibility (Phase 56).
"""
import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.epigenomics import (
    DBEpigenomicExperiment,
    DBChromatinPeak,
    DBTranscriptionFactorMotif,
)


class EpigenomicsRepository:
    """Handles CRUD operations for epigenomics experiments and chromatin accessibility peaks."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_experiment(
        self,
        sample_id: str,
        tissue_type: str,
        assay_type: str = "ATAC-seq",
        sequencing_depth_millions: float = 45.0,
        metadata_info: Optional[Dict[str, Any]] = None,
    ) -> DBEpigenomicExperiment:
        exp = DBEpigenomicExperiment(
            id=str(uuid.uuid4()),
            sample_id=sample_id,
            tissue_type=tissue_type,
            assay_type=assay_type,
            sequencing_depth_millions=sequencing_depth_millions,
            metadata_info=metadata_info or {},
        )
        self.session.add(exp)
        await self.session.flush()
        await self.session.commit()
        return exp

    async def add_peaks_with_motifs(
        self,
        experiment_id: str,
        peaks_data: List[Dict[str, Any]],
    ) -> List[DBChromatinPeak]:
        created_peaks = []
        for p in peaks_data:
            peak = DBChromatinPeak(
                id=str(uuid.uuid4()),
                experiment_id=experiment_id,
                chromosome=p.get("chromosome", "chr1"),
                start_pos=p["start_pos"],
                end_pos=p["end_pos"],
                peak_score=p.get("peak_score", 120.0),
                fold_enrichment=p.get("fold_enrichment", 8.5),
                p_value_neg_log10=p.get("p_value_neg_log10", 15.2),
                genomic_annotation=p.get("genomic_annotation", "Promoter"),
                nearest_gene=p.get("nearest_gene", "GENE"),
                distance_to_tss=p.get("distance_to_tss", 0),
            )
            self.session.add(peak)
            await self.session.flush()

            for m in p.get("motifs", []):
                motif = DBTranscriptionFactorMotif(
                    id=str(uuid.uuid4()),
                    peak_id=peak.id,
                    motif_name=m["motif_name"],
                    pwm_match_score=m.get("pwm_match_score", 0.92),
                    motif_p_value=m.get("motif_p_value", 1e-5),
                    strand=m.get("strand", "+"),
                    consensus_sequence=m.get("consensus_sequence", "TGACTCA"),
                )
                self.session.add(motif)

            created_peaks.append(peak)

        exp = await self.get_experiment(experiment_id)
        if exp:
            exp.total_peaks_called = len(created_peaks)
            self.session.add(exp)

        await self.session.commit()
        return created_peaks

    async def get_experiment(self, experiment_id: str) -> Optional[DBEpigenomicExperiment]:
        self.session.expire_all()
        query = (
            select(DBEpigenomicExperiment)
            .options(
                selectinload(DBEpigenomicExperiment.peaks).selectinload(DBChromatinPeak.motifs)
            )
            .where(DBEpigenomicExperiment.id == experiment_id)
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def list_experiments(self, limit: int = 50) -> List[DBEpigenomicExperiment]:
        query = (
            select(DBEpigenomicExperiment)
            .options(selectinload(DBEpigenomicExperiment.peaks))
            .order_by(desc(DBEpigenomicExperiment.created_at))
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def query_peaks(
        self,
        experiment_id: str,
        chromosome: Optional[str] = None,
        annotation: Optional[str] = None,
        limit: int = 100,
    ) -> List[DBChromatinPeak]:
        query = (
            select(DBChromatinPeak)
            .options(selectinload(DBChromatinPeak.motifs))
            .where(DBChromatinPeak.experiment_id == experiment_id)
        )
        if chromosome:
            query = query.where(DBChromatinPeak.chromosome == chromosome)
        if annotation:
            query = query.where(DBChromatinPeak.genomic_annotation == annotation)

        query = query.order_by(desc(DBChromatinPeak.peak_score)).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())
