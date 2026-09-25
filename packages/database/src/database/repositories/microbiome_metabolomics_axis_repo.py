"""Repository for Phase 182: Gut Microbiome-Host Co-Metabolism & SCFA Dynamics."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.microbiome_metabolomics_axis import MicrobiomeMetabolomicsStudy, MicrobiomeTaxaAbundance, MicrobiomeSCFAKinetics


class MicrobiomeMetabolomicsAxisRepository:
    """Database operations for gut microbiome metabolomics studies."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_study(
        self,
        name: str,
        cohort_sample_id: str,
        dietary_fiber_intake_g_day: float = 32.0,
        firmicutes_bacteroidetes_ratio: float = 1.85,
        total_scfa_concentration_mm: float = 85.4,
        butyrate_acetate_propionate_ratio: str = "60:25:15",
        gut_barrier_integrity_score: float = 0.91,
        secondary_bile_acid_conversion_rate: float = 0.74,
        shannon_diversity_index: float = 3.82,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> MicrobiomeMetabolomicsStudy:
        study = MicrobiomeMetabolomicsStudy(
            name=name,
            cohort_sample_id=cohort_sample_id,
            dietary_fiber_intake_g_day=dietary_fiber_intake_g_day,
            firmicutes_bacteroidetes_ratio=firmicutes_bacteroidetes_ratio,
            total_scfa_concentration_mm=total_scfa_concentration_mm,
            butyrate_acetate_propionate_ratio=butyrate_acetate_propionate_ratio,
            gut_barrier_integrity_score=gut_barrier_integrity_score,
            secondary_bile_acid_conversion_rate=secondary_bile_acid_conversion_rate,
            shannon_diversity_index=shannon_diversity_index,
            status=status,
            parameters=parameters or {},
            summary_report=summary_report,
        )
        self.session.add(study)
        await self.session.flush()
        await self.session.refresh(study)
        return study

    async def add_taxa_abundance(
        self,
        study_id: UUID,
        taxon_name: str,
        phylum: str,
        relative_abundance_pct: float,
        butyrate_synthesis_pathway: str = "butyryl-CoA:acetate CoA-transferase",
        mucosal_adherence_index: float = 0.88,
    ) -> MicrobiomeTaxaAbundance:
        item = MicrobiomeTaxaAbundance(
            study_id=study_id,
            taxon_name=taxon_name,
            phylum=phylum,
            relative_abundance_pct=relative_abundance_pct,
            butyrate_synthesis_pathway=butyrate_synthesis_pathway,
            mucosal_adherence_index=mucosal_adherence_index,
        )
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def add_scfa_kinetic(
        self,
        study_id: UUID,
        metabolite_name: str,
        lumen_concentration_mm: float,
        portal_vein_absorption_rate: float,
        anti_inflammatory_index: float,
        gpr41_43_agonist_potency: float = 0.85,
    ) -> MicrobiomeSCFAKinetics:
        item = MicrobiomeSCFAKinetics(
            study_id=study_id,
            metabolite_name=metabolite_name,
            lumen_concentration_mm=lumen_concentration_mm,
            portal_vein_absorption_rate=portal_vein_absorption_rate,
            anti_inflammatory_index=anti_inflammatory_index,
            gpr41_43_agonist_potency=gpr41_43_agonist_potency,
        )
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def get_study(self, study_id: UUID) -> Optional[MicrobiomeMetabolomicsStudy]:
        stmt = select(MicrobiomeMetabolomicsStudy).where(MicrobiomeMetabolomicsStudy.id == study_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_studies(self, limit: int = 50) -> List[MicrobiomeMetabolomicsStudy]:
        stmt = select(MicrobiomeMetabolomicsStudy).order_by(MicrobiomeMetabolomicsStudy.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())