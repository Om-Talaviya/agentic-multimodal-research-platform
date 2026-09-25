"""Repository for Phase 179: circRNA Biogenesis & miRNA Sponge Matrix."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.circrna_biogenesis import CircRNABiogenesisStudy, CircRNABackspliceJunction, CircRNAMiRNASpongeTarget


class CircRNABiogenesisRepository:
    """Database operations for circRNA biogenesis studies."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_study(
        self,
        name: str,
        host_gene_symbol: str,
        genomic_locus: str,
        exon_count: int = 3,
        flanking_alu_elements_count: int = 2,
        backsplice_efficiency_score: float = 0.88,
        circular_form_half_life_hours: float = 48.5,
        total_mirna_sponge_binding_sites: int = 14,
        quaking_rbp_affinity_score: float = 0.92,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> CircRNABiogenesisStudy:
        study = CircRNABiogenesisStudy(
            name=name,
            host_gene_symbol=host_gene_symbol,
            genomic_locus=genomic_locus,
            exon_count=exon_count,
            flanking_alu_elements_count=flanking_alu_elements_count,
            backsplice_efficiency_score=backsplice_efficiency_score,
            circular_form_half_life_hours=circular_form_half_life_hours,
            total_mirna_sponge_binding_sites=total_mirna_sponge_binding_sites,
            quaking_rbp_affinity_score=quaking_rbp_affinity_score,
            status=status,
            parameters=parameters or {},
            summary_report=summary_report,
        )
        self.session.add(study)
        await self.session.flush()
        await self.session.refresh(study)
        return study

    async def add_backsplice_junction(
        self,
        study_id: UUID,
        junction_id: str,
        donor_exon: int,
        acceptor_exon: int,
        junction_sequence: str,
        junction_reads_ratio: float = 0.34,
        flanking_repeat_match_score: float = 0.91,
    ) -> CircRNABackspliceJunction:
        item = CircRNABackspliceJunction(
            study_id=study_id,
            junction_id=junction_id,
            donor_exon=donor_exon,
            acceptor_exon=acceptor_exon,
            junction_sequence=junction_sequence,
            junction_reads_ratio=junction_reads_ratio,
            flanking_repeat_match_score=flanking_repeat_match_score,
        )
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def add_mirna_sponge_target(
        self,
        study_id: UUID,
        mirna_family: str,
        binding_site_start: int,
        binding_site_end: int,
        seed_match_type: str = "8mer",
        binding_free_energy_kcal_mol: float = -24.5,
        inhibition_potency_score: float = 0.94,
    ) -> CircRNAMiRNASpongeTarget:
        item = CircRNAMiRNASpongeTarget(
            study_id=study_id,
            mirna_family=mirna_family,
            binding_site_start=binding_site_start,
            binding_site_end=binding_site_end,
            seed_match_type=seed_match_type,
            binding_free_energy_kcal_mol=binding_free_energy_kcal_mol,
            inhibition_potency_score=inhibition_potency_score,
        )
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def get_study(self, study_id: UUID) -> Optional[CircRNABiogenesisStudy]:
        stmt = select(CircRNABiogenesisStudy).where(CircRNABiogenesisStudy.id == study_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_studies(self, limit: int = 50) -> List[CircRNABiogenesisStudy]:
        stmt = select(CircRNABiogenesisStudy).order_by(CircRNABiogenesisStudy.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
