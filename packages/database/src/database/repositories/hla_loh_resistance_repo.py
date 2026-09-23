"""
Repository for Phase 135: Cancer Immunogenomics HLA Loss of Heterozygosity (LOH) & Immune Evasion Engine.
"""

import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from database.models.hla_loh_resistance import (
    DBHLALOHStudy,
    DBAlleleCopyNumberProfile,
    DBImmuneEvasionScore,
)


class HLALOHResistanceRepository:
    """Repository handling CRUD operations for HLA LOH studies, allele profiles, and immune evasion scores."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        patient_cohort_id: str,
        tumor_type: str,
        total_alleles_analyzed: int = 6,
        loh_positive_allele_count: int = 2,
        overall_immune_evasion_index: float = 0.74,
        checkpoint_resistance_prediction: str = "High Resistance",
        metadata_json: Optional[Dict[str, Any]] = None,
        project_id: Optional[uuid.UUID] = None,
    ) -> DBHLALOHStudy:
        """Create a new HLA LOH study record."""
        study = DBHLALOHStudy(
            id=uuid.uuid4(),
            project_id=project_id,
            patient_cohort_id=patient_cohort_id,
            tumor_type=tumor_type,
            total_alleles_analyzed=total_alleles_analyzed,
            loh_positive_allele_count=loh_positive_allele_count,
            overall_immune_evasion_index=overall_immune_evasion_index,
            checkpoint_resistance_prediction=checkpoint_resistance_prediction,
            metadata_json=metadata_json or {},
        )
        self.session.add(study)
        await self.session.commit()
        await self.session.refresh(study)
        return study

    async def get_study(self, study_id: uuid.UUID) -> Optional[DBHLALOHStudy]:
        """Get HLA LOH study with allele copy number profiles and evasion scores."""
        stmt = (
            select(DBHLALOHStudy)
            .options(
                selectinload(DBHLALOHStudy.allele_profiles),
                selectinload(DBHLALOHStudy.evasion_scores),
            )
            .where(DBHLALOHStudy.id == study_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[DBHLALOHStudy]:
        """List all HLA LOH studies."""
        stmt = (
            select(DBHLALOHStudy)
            .order_by(desc(DBHLALOHStudy.created_at))
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_allele_profile(
        self,
        study_id: uuid.UUID,
        hla_gene: str,
        allele_identifier: str,
        tumor_copy_number: float,
        germline_copy_number: float = 1.0,
        b_allele_frequency_baf: float = 0.08,
        loh_status: str = "DELETED",
    ) -> DBAlleleCopyNumberProfile:
        """Add an allele-specific copy number profile."""
        profile = DBAlleleCopyNumberProfile(
            id=uuid.uuid4(),
            study_id=study_id,
            hla_gene=hla_gene,
            allele_identifier=allele_identifier,
            tumor_copy_number=tumor_copy_number,
            germline_copy_number=germline_copy_number,
            b_allele_frequency_baf=b_allele_frequency_baf,
            loh_status=loh_status,
        )
        self.session.add(profile)
        await self.session.commit()
        await self.session.refresh(profile)
        return profile

    async def add_evasion_score(
        self,
        study_id: uuid.UUID,
        neoantigen_presentation_loss_percent: float,
        cd8_t_cell_evasion_probability: float,
        nk_cell_activation_potential: float,
        recommended_synthetic_rescue: str = "NK-Engager BiKE or Class II Neoantigen Vaccine",
    ) -> DBImmuneEvasionScore:
        """Add immune evasion metrics."""
        score = DBImmuneEvasionScore(
            id=uuid.uuid4(),
            study_id=study_id,
            neoantigen_presentation_loss_percent=neoantigen_presentation_loss_percent,
            cd8_t_cell_evasion_probability=cd8_t_cell_evasion_probability,
            nk_cell_activation_potential=nk_cell_activation_potential,
            recommended_synthetic_rescue=recommended_synthetic_rescue,
        )
        self.session.add(score)
        await self.session.commit()
        await self.session.refresh(score)
        return score
