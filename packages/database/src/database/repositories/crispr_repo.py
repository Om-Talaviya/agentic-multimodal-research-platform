"""Autonomous Synthetic Biology & CRISPR Gene Editing Guide RNA Repository (Phase 40)."""

import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.crispr import (
    DBBaseEditingProfile,
    DBCRISPRDesign,
    DBGuideRNA,
    DBOffTargetSite,
)
from shared.logging import get_logger

logger = get_logger(__name__)


class CRISPRRepository:
    """Async repository for CRISPR guide designs, on-target efficiency, off-target loci, and base editing profiles."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_design(
        self,
        user_id: uuid.UUID | str,
        target_gene: str,
        genomic_locus: str = "Chr1:55039447-55064852",
        organism: str = "Homo sapiens",
        cas_enzyme: str = "SpCas9",
        pam_motif: str = "NGG",
        target_strand: str = "both",
        editing_modality: str = "knockout_cleavage",
        target_sequence_fasta: str = "",
        design_summary_json: Optional[Dict[str, Any]] = None,
        workspace_id: Optional[uuid.UUID | str] = None,
        project_id: Optional[uuid.UUID | str] = None,
    ) -> DBCRISPRDesign:
        """Create and persist a master CRISPR design campaign."""
        design = DBCRISPRDesign(
            id=uuid.uuid4(),
            user_id=user_id,
            workspace_id=workspace_id,
            project_id=project_id,
            target_gene=target_gene.strip(),
            genomic_locus=genomic_locus.strip(),
            organism=organism.strip(),
            cas_enzyme=cas_enzyme.strip(),
            pam_motif=pam_motif.strip(),
            target_strand=target_strand,
            editing_modality=editing_modality,
            target_sequence_fasta=target_sequence_fasta.strip(),
            design_summary_json=design_summary_json or {},
        )
        self._session.add(design)
        await self._session.flush()
        logger.info(
            "crispr_design_created",
            design_id=str(design.id),
            target_gene=design.target_gene,
            cas_enzyme=design.cas_enzyme,
        )
        return design

    async def get_design(self, design_id: uuid.UUID | str) -> Optional[DBCRISPRDesign]:
        """Fetch CRISPR design with all candidate guide RNAs, off-target sites, and base editing profiles."""
        stmt = (
            select(DBCRISPRDesign)
            .where(DBCRISPRDesign.id == design_id)
            .options(
                selectinload(DBCRISPRDesign.guide_rnas).selectinload(DBGuideRNA.off_target_sites),
                selectinload(DBCRISPRDesign.guide_rnas).selectinload(DBGuideRNA.base_editing_profiles),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_designs(
        self,
        user_id: Optional[uuid.UUID | str] = None,
        workspace_id: Optional[uuid.UUID | str] = None,
        project_id: Optional[uuid.UUID | str] = None,
        target_gene: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[DBCRISPRDesign]:
        """List CRISPR design campaigns with optional filtering."""
        stmt = select(DBCRISPRDesign).options(selectinload(DBCRISPRDesign.guide_rnas))

        if user_id:
            stmt = stmt.where(DBCRISPRDesign.user_id == user_id)
        if workspace_id:
            stmt = stmt.where(DBCRISPRDesign.workspace_id == workspace_id)
        if project_id:
            stmt = stmt.where(DBCRISPRDesign.project_id == project_id)
        if target_gene:
            stmt = stmt.where(DBCRISPRDesign.target_gene.ilike(f"%{target_gene}%"))

        stmt = stmt.order_by(desc(DBCRISPRDesign.created_at)).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def add_guide_rnas(
        self,
        design_id: uuid.UUID | str,
        guides_data: List[Dict[str, Any]],
    ) -> List[DBGuideRNA]:
        """Add candidate guide RNAs to a CRISPR design campaign."""
        created_guides: List[DBGuideRNA] = []
        for g in guides_data:
            guide = DBGuideRNA(
                id=g.get("id") or uuid.uuid4(),
                design_id=design_id,
                guide_name=g["guide_name"],
                spacer_sequence_20nt=g["spacer_sequence_20nt"],
                pam_sequence=g["pam_sequence"],
                genomic_position=g.get("genomic_position", 0),
                strand=g.get("strand", "+"),
                cut_position_rel=g.get("cut_position_rel", 17),
                on_target_efficiency_score=g.get("on_target_efficiency_score", 80.0),
                off_target_cfd_score=g.get("off_target_cfd_score", 90.0),
                gc_content_pct=g.get("gc_content_pct", 50.0),
                secondary_structure_delta_g=g.get("secondary_structure_delta_g", -2.0),
                recommendation_tier=g.get("recommendation_tier", "optimal"),
                oligo_forward_top=g.get("oligo_forward_top", ""),
                oligo_reverse_bottom=g.get("oligo_reverse_bottom", ""),
            )
            self._session.add(guide)
            created_guides.append(guide)

        await self._session.flush()
        return created_guides

    async def add_off_target_sites(
        self,
        guide_id: uuid.UUID | str,
        off_targets_data: List[Dict[str, Any]],
    ) -> List[DBOffTargetSite]:
        """Persist predicted off-target mismatch loci for a specific guide RNA."""
        created_sites: List[DBOffTargetSite] = []
        for site in off_targets_data:
            off_target = DBOffTargetSite(
                id=uuid.uuid4(),
                guide_id=guide_id,
                chromosome=site["chromosome"],
                genomic_coordinate=site["genomic_coordinate"],
                mismatched_sequence=site["mismatched_sequence"],
                mismatch_count=site.get("mismatch_count", 2),
                mismatch_positions_json=site.get("mismatch_positions_json", []),
                cfd_cleavage_score=site.get("cfd_cleavage_score", 0.05),
                gene_annotation=site.get("gene_annotation", "Intergenic"),
                is_exonic=site.get("is_exonic", False),
            )
            self._session.add(off_target)
            created_sites.append(off_target)

        await self._session.flush()
        return created_sites

    async def add_base_editing_profiles(
        self,
        guide_id: uuid.UUID | str,
        profiles_data: List[Dict[str, Any]],
    ) -> List[DBBaseEditingProfile]:
        """Persist base editing (ABE/CBE) window predictions for a specific guide RNA."""
        created_profiles: List[DBBaseEditingProfile] = []
        for prof in profiles_data:
            profile = DBBaseEditingProfile(
                id=uuid.uuid4(),
                guide_id=guide_id,
                editing_type=prof.get("editing_type", "ABE_A_to_G"),
                target_base=prof.get("target_base", "A"),
                editing_window_start=prof.get("editing_window_start", 4),
                editing_window_end=prof.get("editing_window_end", 8),
                expected_product_sequence=prof["expected_product_sequence"],
                bystander_bases_count=prof.get("bystander_bases_count", 0),
                purity_score_pct=prof.get("purity_score_pct", 90.0),
                activity_score_pct=prof.get("activity_score_pct", 75.0),
            )
            self._session.add(profile)
            created_profiles.append(profile)

        await self._session.flush()
        return created_profiles

    async def get_guide(self, guide_id: uuid.UUID | str) -> Optional[DBGuideRNA]:
        """Fetch a specific guide RNA by ID."""
        stmt = select(DBGuideRNA).where(DBGuideRNA.id == guide_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_design(self, design_id: uuid.UUID | str) -> bool:
        """Delete a CRISPR design campaign and cascaded children."""
        stmt = select(DBCRISPRDesign).where(DBCRISPRDesign.id == design_id)
        result = await self._session.execute(stmt)
        design = result.scalar_one_or_none()
        if not design:
            return False
        await self._session.delete(design)
        await self._session.flush()
        return True
