"""
Repository for Phase 138: High-Throughput Lipid Nanoparticle (LNP) Formulation & mRNA Encapsulation Efficiency Engine.
"""

import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from database.models.lnp_encapsulation import (
    DBLNPFormulationScreen,
    DBLipidRatioComponent,
    DBEncapsulationEfficiencyMetric,
)


class LNPEncapsulationRepository:
    """Repository handling CRUD operations for LNP formulation screens, lipid molar ratios, and encapsulation metrics."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_screen(
        self,
        formulation_tag: str,
        mrna_payload_name: str = "EGFP Reporter / Antigen mRNA",
        flow_rate_ratio_aqueous_to_organic: float = 3.0,
        total_flow_rate_ml_min: float = 12.0,
        nitrogen_to_phosphate_np_ratio: float = 6.0,
        hydrodynamic_diameter_pdi: float = 0.08,
        particle_size_z_avg_nm: float = 74.5,
        encapsulation_efficiency_percent: float = 94.2,
        metadata_json: Optional[Dict[str, Any]] = None,
        project_id: Optional[uuid.UUID] = None,
    ) -> DBLNPFormulationScreen:
        """Create a new LNP formulation screen record."""
        screen = DBLNPFormulationScreen(
            id=uuid.uuid4(),
            project_id=project_id,
            formulation_tag=formulation_tag,
            mrna_payload_name=mrna_payload_name,
            flow_rate_ratio_aqueous_to_organic=flow_rate_ratio_aqueous_to_organic,
            total_flow_rate_ml_min=total_flow_rate_ml_min,
            nitrogen_to_phosphate_np_ratio=nitrogen_to_phosphate_np_ratio,
            hydrodynamic_diameter_pdi=hydrodynamic_diameter_pdi,
            particle_size_z_avg_nm=particle_size_z_avg_nm,
            encapsulation_efficiency_percent=encapsulation_efficiency_percent,
            metadata_json=metadata_json or {},
        )
        self.session.add(screen)
        await self.session.commit()
        await self.session.refresh(screen)
        return screen

    async def get_screen(self, screen_id: uuid.UUID) -> Optional[DBLNPFormulationScreen]:
        """Get LNP formulation screen with lipid components and efficiency metrics."""
        stmt = (
            select(DBLNPFormulationScreen)
            .options(
                selectinload(DBLNPFormulationScreen.lipid_components),
                selectinload(DBLNPFormulationScreen.efficiency_metrics),
            )
            .where(DBLNPFormulationScreen.id == screen_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_screens(self, limit: int = 50, offset: int = 0) -> List[DBLNPFormulationScreen]:
        """List all LNP formulation screens."""
        stmt = (
            select(DBLNPFormulationScreen)
            .order_by(desc(DBLNPFormulationScreen.created_at))
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_lipid_component(
        self,
        formulation_id: uuid.UUID,
        lipid_type: str,
        mol_percent: float,
        pka_apparent: Optional[float] = None,
    ) -> DBLipidRatioComponent:
        """Add a lipid component molar ratio."""
        comp = DBLipidRatioComponent(
            id=uuid.uuid4(),
            formulation_id=formulation_id,
            lipid_type=lipid_type,
            mol_percent=mol_percent,
            pka_apparent=pka_apparent,
        )
        self.session.add(comp)
        await self.session.commit()
        await self.session.refresh(comp)
        return comp

    async def add_efficiency_metric(
        self,
        formulation_id: uuid.UUID,
        ribogreen_free_rna_fluorescence: float,
        ribogreen_total_rna_fluorescence: float,
        calculated_encapsulation_percent: float,
        cryo_tem_morphology: str = "Homogeneous Electron-Dense Core",
        in_vivo_transfection_potency_fold: float = 8.2,
    ) -> DBEncapsulationEfficiencyMetric:
        """Add RiboGreen assay metric."""
        metric = DBEncapsulationEfficiencyMetric(
            id=uuid.uuid4(),
            formulation_id=formulation_id,
            ribogreen_free_rna_fluorescence=ribogreen_free_rna_fluorescence,
            ribogreen_total_rna_fluorescence=ribogreen_total_rna_fluorescence,
            calculated_encapsulation_percent=calculated_encapsulation_percent,
            cryo_tem_morphology=cryo_tem_morphology,
            in_vivo_transfection_potency_fold=in_vivo_transfection_potency_fold,
        )
        self.session.add(metric)
        await self.session.commit()
        await self.session.refresh(metric)
        return metric
