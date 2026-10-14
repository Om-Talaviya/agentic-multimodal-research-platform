"""Repository for Phase 495: Autonomous Spatial Multi-Modal Epigenomic CUT&Tag-RNA Joint Profiling Diffusion Trajectory Mapper."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.cuttag_rna_joint_diffusion_trajectory import (
    CuttagRnaJointDiffusionTrajectoryStudy,
    CuttagRnaJointDiffusionTrajectoryItemProfile,
    CuttagRnaJointDiffusionTrajectoryMetricTrace,
)


class CuttagRnaJointDiffusionTrajectoryRepository:
    """Database operations for Autonomous Spatial Multi-Modal Epigenomic CUT&Tag-RNA Joint Profiling Diffusion Trajectory Mapper."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Developing Murine Cortical Plate Radial Glia Lineage with H3K4me3 / H3K27ac and mRNA Co-Assay",
        analytical_modality: str = "cuttag-rna-joint-diffusion",
        epigenomic_chromatin_velocity_coherence: float = 0.932,
        promoter_enhancer_concordance_score: float = 0.895,
        diffusion_pseudotime_lineage_resolution_tau: float = 0.965,
        joint_latent_space_neighbor_overlap_pct: float = 94.2,
        confidence_score: float = 0.992,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> CuttagRnaJointDiffusionTrajectoryStudy:
        study = CuttagRnaJointDiffusionTrajectoryStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            epigenomic_chromatin_velocity_coherence=epigenomic_chromatin_velocity_coherence,
            promoter_enhancer_concordance_score=promoter_enhancer_concordance_score,
            diffusion_pseudotime_lineage_resolution_tau=diffusion_pseudotime_lineage_resolution_tau,
            joint_latent_space_neighbor_overlap_pct=joint_latent_space_neighbor_overlap_pct,
            confidence_score=confidence_score,
            status=status,
            parameters=parameters or {},
            summary_report=summary_report,
        )
        self.session.add(study)
        await self.session.flush()
        await self.session.refresh(study)
        return study

    async def add_item_profile(
        self,
        study_id: UUID,
        item_name: str,
        profile_category: str = "Analysis Profile",
        quantitative_value: float = 1.0,
        log2_fold_change: float = 1.5,
        significance_score: float = 0.95,
    ) -> CuttagRnaJointDiffusionTrajectoryItemProfile:
        item = CuttagRnaJointDiffusionTrajectoryItemProfile(
            study_id=study_id,
            item_name=item_name,
            profile_category=profile_category,
            quantitative_value=quantitative_value,
            log2_fold_change=log2_fold_change,
            significance_score=significance_score,
        )
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def add_metric_trace(
        self,
        study_id: UUID,
        metric_dimension: str,
        observed_value: float,
        z_score: float = 0.0,
        p_value: float = 0.05,
    ) -> CuttagRnaJointDiffusionTrajectoryMetricTrace:
        trace = CuttagRnaJointDiffusionTrajectoryMetricTrace(
            study_id=study_id,
            metric_dimension=metric_dimension,
            observed_value=observed_value,
            z_score=z_score,
            p_value=p_value,
        )
        self.session.add(trace)
        await self.session.flush()
        await self.session.refresh(trace)
        return trace

    async def get_study(self, study_id: UUID) -> Optional[CuttagRnaJointDiffusionTrajectoryStudy]:
        result = await self.session.execute(
            select(CuttagRnaJointDiffusionTrajectoryStudy)
            .options(
                selectinload(CuttagRnaJointDiffusionTrajectoryStudy.item_profiles),
                selectinload(CuttagRnaJointDiffusionTrajectoryStudy.metric_traces),
            )
            .where(CuttagRnaJointDiffusionTrajectoryStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[CuttagRnaJointDiffusionTrajectoryStudy]:
        result = await self.session.execute(
            select(CuttagRnaJointDiffusionTrajectoryStudy)
            .options(
                selectinload(CuttagRnaJointDiffusionTrajectoryStudy.item_profiles),
                selectinload(CuttagRnaJointDiffusionTrajectoryStudy.metric_traces),
            )
            .order_by(CuttagRnaJointDiffusionTrajectoryStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
