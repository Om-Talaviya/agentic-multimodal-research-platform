"""
Phase 126: Autonomous Whole-Genome Long-Read Telomere-to-Telomere Structural Variant Repository.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
import uuid

from database.models.t2t_assembly import (
    DBT2TAssembly,
    DBT2TStructuralVariantCall,
    DBPhasedHaplotypeBlock,
)


class T2TAssemblyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_assembly(
        self,
        sample_name: str,
        sequencing_technology: str = "PacBio-HiFi+ONT-UltraLong",
        total_contig_length_bp: int = 3117275501,
        n50_length_kbp: float = 145200.5,
        qv_consensus_accuracy: float = 62.4,
        kmer_completeness_pct: float = 99.98,
        telomere_telomere_closed_chromosomes: int = 24,
        metadata_json: Optional[Dict[str, Any]] = None,
        project_id: Optional[str] = None,
    ) -> DBT2TAssembly:
        assembly = DBT2TAssembly(
            id=uuid.uuid4(),
            project_id=project_id,
            sample_name=sample_name,
            sequencing_technology=sequencing_technology,
            total_contig_length_bp=total_contig_length_bp,
            n50_length_kbp=n50_length_kbp,
            qv_consensus_accuracy=qv_consensus_accuracy,
            kmer_completeness_pct=kmer_completeness_pct,
            telomere_telomere_closed_chromosomes=telomere_telomere_closed_chromosomes,
            metadata_json=metadata_json or {},
        )
        self.session.add(assembly)
        await self.session.commit()
        await self.session.refresh(assembly)
        return assembly

    async def get_assembly(self, assembly_id: uuid.UUID) -> Optional[DBT2TAssembly]:
        stmt = (
            select(DBT2TAssembly)
            .options(
                selectinload(DBT2TAssembly.variants),
                selectinload(DBT2TAssembly.haplotypes),
            )
            .where(DBT2TAssembly.id == assembly_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_assemblies(self, limit: int = 50) -> List[DBT2TAssembly]:
        stmt = (
            select(DBT2TAssembly)
            .options(
                selectinload(DBT2TAssembly.variants),
                selectinload(DBT2TAssembly.haplotypes),
            )
            .order_by(desc(DBT2TAssembly.created_at))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_structural_variant(
        self,
        assembly_id: uuid.UUID,
        variant_id: str,
        chromosome: str,
        start_position: int,
        end_position: int,
        sv_type: str,
        sv_length_bp: int,
        genotype_quality: float = 99.0,
        supporting_reads_count: int = 45,
        flanking_repeat_motif: Optional[str] = None,
        functional_impact_score: float = 0.75,
    ) -> DBT2TStructuralVariantCall:
        sv = DBT2TStructuralVariantCall(
            id=uuid.uuid4(),
            assembly_id=assembly_id,
            variant_id=variant_id,
            chromosome=chromosome,
            start_position=start_position,
            end_position=end_position,
            sv_type=sv_type,
            sv_length_bp=sv_length_bp,
            genotype_quality=genotype_quality,
            supporting_reads_count=supporting_reads_count,
            flanking_repeat_motif=flanking_repeat_motif,
            functional_impact_score=functional_impact_score,
        )
        self.session.add(sv)
        await self.session.commit()
        await self.session.refresh(sv)
        return sv

    async def add_haplotype_block(
        self,
        assembly_id: uuid.UUID,
        chromosome: str,
        block_start_bp: int,
        block_end_bp: int,
        phase_switch_error_rate: float = 0.0012,
        maternal_markers_count: int = 12400,
        paternal_markers_count: int = 11980,
    ) -> DBPhasedHaplotypeBlock:
        block = DBPhasedHaplotypeBlock(
            id=uuid.uuid4(),
            assembly_id=assembly_id,
            chromosome=chromosome,
            block_start_bp=block_start_bp,
            block_end_bp=block_end_bp,
            phase_switch_error_rate=phase_switch_error_rate,
            maternal_markers_count=maternal_markers_count,
            paternal_markers_count=paternal_markers_count,
        )
        self.session.add(block)
        await self.session.commit()
        await self.session.refresh(block)
        return block
