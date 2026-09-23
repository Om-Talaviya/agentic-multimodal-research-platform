"""
Repository for Phase 137: CAR-Macrophage (CAR-M) Solid Tumor Phagocytosis & TME Matrix Degradation Engine.
"""

import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from database.models.car_macrophage import (
    DBCARMacrophageDesign,
    DBPhagocytosisKinetics,
    DBTMERepolarizationProfile,
)


class CARMacrophageRepository:
    """Repository handling CRUD operations for CAR-Macrophage constructs, phagocytosis kinetics, and TME repolarization."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_design(
        self,
        construct_name: str,
        target_tumor_antigen: str = "HER2 / ERBB2",
        scfv_domain: str = "Trastuzumab-derived 4D5",
        intracellular_signaling_domain: str = "Megf10 / FcR-gamma",
        macrophage_subtype: str = "M1-Polarized Pro-Inflammatory",
        matrix_degradation_mmp_score: float = 8.4,
        target_phagocytosis_efficiency_percent: float = 78.5,
        metadata_json: Optional[Dict[str, Any]] = None,
        project_id: Optional[uuid.UUID] = None,
    ) -> DBCARMacrophageDesign:
        """Create a new CAR-Macrophage construct design."""
        design = DBCARMacrophageDesign(
            id=uuid.uuid4(),
            project_id=project_id,
            construct_name=construct_name,
            target_tumor_antigen=target_tumor_antigen,
            scfv_domain=scfv_domain,
            intracellular_signaling_domain=intracellular_signaling_domain,
            macrophage_subtype=macrophage_subtype,
            matrix_degradation_mmp_score=matrix_degradation_mmp_score,
            target_phagocytosis_efficiency_percent=target_phagocytosis_efficiency_percent,
            metadata_json=metadata_json or {},
        )
        self.session.add(design)
        await self.session.commit()
        await self.session.refresh(design)
        return design

    async def get_design(self, design_id: uuid.UUID) -> Optional[DBCARMacrophageDesign]:
        """Get CAR-Macrophage design with phagocytosis and TME profiles."""
        stmt = (
            select(DBCARMacrophageDesign)
            .options(
                selectinload(DBCARMacrophageDesign.phagocytosis_records),
                selectinload(DBCARMacrophageDesign.tme_profiles),
            )
            .where(DBCARMacrophageDesign.id == design_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_designs(self, limit: int = 50, offset: int = 0) -> List[DBCARMacrophageDesign]:
        """List all CAR-Macrophage designs."""
        stmt = (
            select(DBCARMacrophageDesign)
            .order_by(desc(DBCARMacrophageDesign.created_at))
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_phagocytosis_record(
        self,
        design_id: uuid.UUID,
        target_cell_line: str,
        effector_to_target_ratio: str = "2:1",
        trogocytosis_rate_percent: float = 12.4,
        whole_cell_engulfment_rate_percent: float = 66.1,
        antigen_cross_presentation_index: float = 0.88,
    ) -> DBPhagocytosisKinetics:
        """Add phagocytosis kinetics record."""
        record = DBPhagocytosisKinetics(
            id=uuid.uuid4(),
            design_id=design_id,
            target_cell_line=target_cell_line,
            effector_to_target_ratio=effector_to_target_ratio,
            trogocytosis_rate_percent=trogocytosis_rate_percent,
            whole_cell_engulfment_rate_percent=whole_cell_engulfment_rate_percent,
            antigen_cross_presentation_index=antigen_cross_presentation_index,
        )
        self.session.add(record)
        await self.session.commit()
        await self.session.refresh(record)
        return record

    async def add_tme_profile(
        self,
        design_id: uuid.UUID,
        tnf_alpha_secretion_pg_ml: float,
        il12_secretion_pg_ml: float,
        il10_immunosuppression_fold_reduction: float,
        collagen_matrix_clearance_percent: float,
    ) -> DBTMERepolarizationProfile:
        """Add TME repolarization and matrix clearance metrics."""
        profile = DBTMERepolarizationProfile(
            id=uuid.uuid4(),
            design_id=design_id,
            tnf_alpha_secretion_pg_ml=tnf_alpha_secretion_pg_ml,
            il12_secretion_pg_ml=il12_secretion_pg_ml,
            il10_immunosuppression_fold_reduction=il10_immunosuppression_fold_reduction,
            collagen_matrix_clearance_percent=collagen_matrix_clearance_percent,
        )
        self.session.add(profile)
        await self.session.commit()
        await self.session.refresh(profile)
        return profile
