"""Repository for Phase 180: CRISPR Prime Editing pegRNA & Flap Kinetics."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.crispr_prime_editing_pegdna import PrimeEditingPegDNAStudy, PegDNASpacerPBSRTTDesign, PegDNAFlapEquilibriumMetric


class CRISPRPrimeEditingPegDNARepository:
    """Database operations for prime editing pegRNA design studies."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_study(
        self,
        name: str,
        target_gene: str,
        intended_mutation_type: str = "point_substitution",
        pbs_length_nt: int = 13,
        rtt_length_nt: int = 15,
        nick_to_edit_distance_bp: int = 3,
        predicted_prime_editing_efficiency: float = 0.68,
        indel_byproduct_frequency: float = 0.035,
        flap_equilibrium_ratio: float = 3.42,
        pe_system_version: str = "PEmax_epegRNA",
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> PrimeEditingPegDNAStudy:
        study = PrimeEditingPegDNAStudy(
            name=name,
            target_gene=target_gene,
            intended_mutation_type=intended_mutation_type,
            pbs_length_nt=pbs_length_nt,
            rtt_length_nt=rtt_length_nt,
            nick_to_edit_distance_bp=nick_to_edit_distance_bp,
            predicted_prime_editing_efficiency=predicted_prime_editing_efficiency,
            indel_byproduct_frequency=indel_byproduct_frequency,
            flap_equilibrium_ratio=flap_equilibrium_ratio,
            pe_system_version=pe_system_version,
            status=status,
            parameters=parameters or {},
            summary_report=summary_report,
        )
        self.session.add(study)
        await self.session.flush()
        await self.session.refresh(study)
        return study

    async def add_pegdna_design(
        self,
        study_id: UUID,
        candidate_id: str,
        spacer_sequence_20nt: str,
        pbs_sequence: str,
        rtt_sequence_with_edit: str,
        tevpre_structural_motif: str = "tevpre_hairpin",
        deep_pe_score: float = 0.84,
        melting_temp_pbs_celsius: float = 38.5,
    ) -> PegDNASpacerPBSRTTDesign:
        item = PegDNASpacerPBSRTTDesign(
            study_id=study_id,
            candidate_id=candidate_id,
            spacer_sequence_20nt=spacer_sequence_20nt,
            pbs_sequence=pbs_sequence,
            rtt_sequence_with_edit=rtt_sequence_with_edit,
            tevpre_structural_motif=tevpre_structural_motif,
            deep_pe_score=deep_pe_score,
            melting_temp_pbs_celsius=melting_temp_pbs_celsius,
        )
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def add_flap_metric(
        self,
        study_id: UUID,
        flap_position_nt: int,
        gibbs_free_energy_edited_flap_kcal: float,
        gibbs_free_energy_unmodified_flap_kcal: float,
        fen1_endonuclease_cleavage_rate: float,
        incorporation_probability: float,
    ) -> PegDNAFlapEquilibriumMetric:
        item = PegDNAFlapEquilibriumMetric(
            study_id=study_id,
            flap_position_nt=flap_position_nt,
            gibbs_free_energy_edited_flap_kcal=gibbs_free_energy_edited_flap_kcal,
            gibbs_free_energy_unmodified_flap_kcal=gibbs_free_energy_unmodified_flap_kcal,
            fen1_endonuclease_cleavage_rate=fen1_endonuclease_cleavage_rate,
            incorporation_probability=incorporation_probability,
        )
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def get_study(self, study_id: UUID) -> Optional[PrimeEditingPegDNAStudy]:
        stmt = select(PrimeEditingPegDNAStudy).where(PrimeEditingPegDNAStudy.id == study_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_studies(self, limit: int = 50) -> List[PrimeEditingPegDNAStudy]:
        stmt = select(PrimeEditingPegDNAStudy).order_by(PrimeEditingPegDNAStudy.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
