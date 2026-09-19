"""Repository for CAR-NK & SynNotch Cell Circuit Designer (Phase 96)."""

import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from database.models.car_nk import (
    DBCarNkDesign,
    DBSynNotchGate,
    DBCytokineSecretionProfile,
)


class CarNkDesignRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_design(
        self,
        workspace_id: uuid.UUID,
        construct_name: str,
        primary_target: str,
        costimulatory_domain: str = "2B4_plus_41BB",
        signaling_domain: str = "CD3zeta",
        cytotoxicity_score: float = 88.5,
        persistence_index: float = 82.0,
        exhaustion_resistance_score: float = 91.4,
        off_tumor_safety_margin: float = 94.0,
        design_metadata: Optional[Dict[str, Any]] = None,
    ) -> DBCarNkDesign:
        design = DBCarNkDesign(
            workspace_id=workspace_id,
            construct_name=construct_name,
            primary_target=primary_target,
            costimulatory_domain=costimulatory_domain,
            signaling_domain=signaling_domain,
            cytotoxicity_score=cytotoxicity_score,
            persistence_index=persistence_index,
            exhaustion_resistance_score=exhaustion_resistance_score,
            off_tumor_safety_margin=off_tumor_safety_margin,
            design_metadata=design_metadata or {},
        )
        self.session.add(design)
        await self.session.commit()
        await self.session.refresh(design)
        return design

    async def add_synnotch_gate(
        self,
        car_nk_id: uuid.UUID,
        gate_type: str,
        sensor_antigen: str,
        actuator_payload: str,
        specificity_enrichment: float = 14.5,
        leaky_expression_pct: float = 1.8,
    ) -> DBSynNotchGate:
        gate = DBSynNotchGate(
            car_nk_id=car_nk_id,
            gate_type=gate_type,
            sensor_antigen=sensor_antigen,
            actuator_payload=actuator_payload,
            specificity_enrichment=specificity_enrichment,
            leaky_expression_pct=leaky_expression_pct,
        )
        self.session.add(gate)
        await self.session.commit()
        await self.session.refresh(gate)
        return gate

    async def add_cytokine_profile(
        self,
        car_nk_id: uuid.UUID,
        cytokine_name: str,
        secretion_level_pg_ml: float,
        is_armored_payload: str = "AUTONOMOUS_SECRETION",
    ) -> DBCytokineSecretionProfile:
        cp = DBCytokineSecretionProfile(
            car_nk_id=car_nk_id,
            cytokine_name=cytokine_name,
            secretion_level_pg_ml=secretion_level_pg_ml,
            is_armored_payload=is_armored_payload,
        )
        self.session.add(cp)
        await self.session.commit()
        await self.session.refresh(cp)
        return cp

    async def get_design(self, design_id: uuid.UUID) -> Optional[DBCarNkDesign]:
        stmt = (
            select(DBCarNkDesign)
            .options(
                selectinload(DBCarNkDesign.synnotch_gates),
                selectinload(DBCarNkDesign.cytokines),
            )
            .where(DBCarNkDesign.id == design_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
