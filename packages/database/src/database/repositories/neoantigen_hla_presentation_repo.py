"""Repository for Phase 185: Tumor Neoantigen & HLA Presentation."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.neoantigen_hla_presentation import NeoantigenHLAStudy, NeoantigenPeptideCandidate, NeoantigenHLABindingPrediction


class NeoantigenHLAPresentationRepository:
    """Database operations for tumor neoantigen HLA presentation studies."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_study(
        self,
        name: str,
        patient_tumor_id: str,
        patient_hla_alleles: str = "HLA-A*02:01, HLA-A*24:02, HLA-B*07:02",
        somatic_mutations_analyzed_count: int = 45,
        high_affinity_neoepitopes_count: int = 8,
        immunogenicity_score_mean: float = 0.86,
        proteasomal_cleavage_efficiency: float = 0.92,
        tap_transport_efficiency: float = 0.88,
        mrna_vaccine_tier1_candidates_count: int = 3,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> NeoantigenHLAStudy:
        study = NeoantigenHLAStudy(
            name=name,
            patient_tumor_id=patient_tumor_id,
            patient_hla_alleles=patient_hla_alleles,
            somatic_mutations_analyzed_count=somatic_mutations_analyzed_count,
            high_affinity_neoepitopes_count=high_affinity_neoepitopes_count,
            immunogenicity_score_mean=immunogenicity_score_mean,
            proteasomal_cleavage_efficiency=proteasomal_cleavage_efficiency,
            tap_transport_efficiency=tap_transport_efficiency,
            mrna_vaccine_tier1_candidates_count=mrna_vaccine_tier1_candidates_count,
            status=status,
            parameters=parameters or {},
            summary_report=summary_report,
        )
        self.session.add(study)
        await self.session.flush()
        await self.session.refresh(study)
        return study

    async def add_peptide_candidate(
        self,
        study_id: UUID,
        gene_symbol: str,
        mutation_syntax: str,
        wildtype_peptide: str,
        mutant_peptide_sequence: str,
        peptide_length: int = 9,
        tcr_recognition_probability: float = 0.85,
    ) -> NeoantigenPeptideCandidate:
        item = NeoantigenPeptideCandidate(
            study_id=study_id,
            gene_symbol=gene_symbol,
            mutation_syntax=mutation_syntax,
            wildtype_peptide=wildtype_peptide,
            mutant_peptide_sequence=mutant_peptide_sequence,
            peptide_length=peptide_length,
            tcr_recognition_probability=tcr_recognition_probability,
        )
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def add_hla_prediction(
        self,
        study_id: UUID,
        peptide_sequence: str,
        hla_allele: str,
        binding_affinity_ic50_nm: float,
        presentation_percentile_rank: float,
        stability_half_life_hours: float,
        is_strong_binder: bool = True,
    ) -> NeoantigenHLABindingPrediction:
        item = NeoantigenHLABindingPrediction(
            study_id=study_id,
            peptide_sequence=peptide_sequence,
            hla_allele=hla_allele,
            binding_affinity_ic50_nm=binding_affinity_ic50_nm,
            presentation_percentile_rank=presentation_percentile_rank,
            stability_half_life_hours=stability_half_life_hours,
            is_strong_binder=is_strong_binder,
        )
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def get_study(self, study_id: UUID) -> Optional[NeoantigenHLAStudy]:
        stmt = select(NeoantigenHLAStudy).where(NeoantigenHLAStudy.id == study_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_studies(self, limit: int = 50) -> List[NeoantigenHLAStudy]:
        stmt = select(NeoantigenHLAStudy).order_by(NeoantigenHLAStudy.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())