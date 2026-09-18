"""Repository for Long-Read Genomics and Telomere Profiling."""
from typing import List, Optional, Dict, Any
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.long_read_genomics import (
    DBLongReadSequencingRun,
    DBStructuralVariantCall,
    DBTelomericRepeatProfile,
)


class LongReadGenomicsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_run(
        self,
        sample_name: str,
        platform: str = "PACBIO_HIFI",
        flowcell_type: str = "PromethION_R10.4.1",
        mean_read_length_bp: float = 18500.0,
        total_gigabases: float = 45.2,
        n50_length_bp: int = 21400,
        mean_phred_quality: float = 31.5,
        run_metadata_json: Optional[Dict[str, Any]] = None,
    ) -> DBLongReadSequencingRun:
        run = DBLongReadSequencingRun(
            sample_name=sample_name,
            platform=platform,
            flowcell_type=flowcell_type,
            mean_read_length_bp=mean_read_length_bp,
            total_gigabases=total_gigabases,
            n50_length_bp=n50_length_bp,
            mean_phred_quality=mean_phred_quality,
            run_metadata_json=run_metadata_json or {},
        )
        self.session.add(run)
        await self.session.commit()
        await self.session.refresh(run)
        return run

    async def add_structural_variant(
        self,
        run_id: str,
        chromosome: str,
        start_pos: int,
        end_pos: int,
        sv_type: str = "DELETION",
        sv_length_bp: int = 1250,
        genotype: str = "0/1",
        support_reads: int = 28,
        filter_status: str = "PASS",
    ) -> DBStructuralVariantCall:
        sv = DBStructuralVariantCall(
            run_id=run_id,
            chromosome=chromosome,
            start_pos=start_pos,
            end_pos=end_pos,
            sv_type=sv_type,
            sv_length_bp=sv_length_bp,
            genotype=genotype,
            support_reads=support_reads,
            filter_status=filter_status,
        )
        self.session.add(sv)
        await self.session.commit()
        await self.session.refresh(sv)
        return sv

    async def add_telomere_profile(
        self,
        run_id: str,
        chromosome_arm: str,
        hexamer_motif: str = "TTAGGG",
        repeat_count: int = 1450,
        telomere_length_kbp: float = 8.7,
        erosion_hazard_level: str = "LOW",
    ) -> DBTelomericRepeatProfile:
        tel = DBTelomericRepeatProfile(
            run_id=run_id,
            chromosome_arm=chromosome_arm,
            hexamer_motif=hexamer_motif,
            repeat_count=repeat_count,
            telomere_length_kbp=telomere_length_kbp,
            erosion_hazard_level=erosion_hazard_level,
        )
        self.session.add(tel)
        await self.session.commit()
        await self.session.refresh(tel)
        return tel

    async def get_run(self, run_id: str) -> Optional[DBLongReadSequencingRun]:
        stmt = (
            select(DBLongReadSequencingRun)
            .where(DBLongReadSequencingRun.id == run_id)
            .options(
                selectinload(DBLongReadSequencingRun.structural_variants),
                selectinload(DBLongReadSequencingRun.telomeric_profiles),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_runs(self, limit: int = 50) -> List[DBLongReadSequencingRun]:
        stmt = (
            select(DBLongReadSequencingRun)
            .options(
                selectinload(DBLongReadSequencingRun.structural_variants),
                selectinload(DBLongReadSequencingRun.telomeric_profiles),
            )
            .order_by(desc(DBLongReadSequencingRun.created_at))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
