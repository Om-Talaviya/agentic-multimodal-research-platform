"""Repository for Whole-Body PBPK Digital Twin & Trans-Organ Pharmacokinetics."""

import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from database.connection import AsyncSession
from database.models.whole_body_pbpk import (
    DBWholeBodyPBPKStudy,
    DBOrganTissueCompartment,
    DBTransOrganClearanceRate,
)


class WholeBodyPBPKRepository:
    """Repository handling CRUD operations for Whole-Body PBPK Digital Twin Studies."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_study(
        self,
        study_name: str,
        drug_candidate_name: str,
        molecular_weight_da: float,
        logp: float,
        plasma_protein_unbound_fraction: float,
        intrinsic_clearance_ml_min_kg: float,
        species: str = "human",
        administration_route: str = "oral",
        dose_mg_kg: float = 10.0,
        simulation_time_hours: float = 24.0,
        summary_metrics: Optional[Dict[str, Any]] = None,
        compartments: Optional[List[Dict[str, Any]]] = None,
        clearance_rates: Optional[List[Dict[str, Any]]] = None,
    ) -> DBWholeBodyPBPKStudy:
        """Create a new PBPK study with organ compartments and clearance pathways."""
        study_id = uuid.uuid4()
        study = DBWholeBodyPBPKStudy(
            id=study_id,
            study_name=study_name,
            drug_candidate_name=drug_candidate_name,
            molecular_weight_da=molecular_weight_da,
            logp=logp,
            plasma_protein_unbound_fraction=plasma_protein_unbound_fraction,
            intrinsic_clearance_ml_min_kg=intrinsic_clearance_ml_min_kg,
            species=species,
            administration_route=administration_route,
            dose_mg_kg=dose_mg_kg,
            simulation_time_hours=simulation_time_hours,
            status="completed",
            summary_metrics=summary_metrics or {},
        )
        self.session.add(study)
        await self.session.flush()

        if compartments:
            for comp in compartments:
                comp_record = DBOrganTissueCompartment(
                    id=uuid.uuid4(),
                    study_id=study_id,
                    organ_name=comp["organ_name"],
                    organ_volume_l_kg=comp["organ_volume_l_kg"],
                    blood_flow_rate_l_h_kg=comp["blood_flow_rate_l_h_kg"],
                    tissue_plasma_partition_coefficient=comp["tissue_plasma_partition_coefficient"],
                    permeability_surface_area_product=comp["permeability_surface_area_product"],
                    computed_cmax_ug_ml=comp["computed_cmax_ug_ml"],
                    computed_auc_ug_h_ml=comp["computed_auc_ug_h_ml"],
                    computed_tmax_h=comp["computed_tmax_h"],
                )
                self.session.add(comp_record)

        if clearance_rates:
            for cl in clearance_rates:
                cl_record = DBTransOrganClearanceRate(
                    id=uuid.uuid4(),
                    study_id=study_id,
                    elimination_pathway=cl["elimination_pathway"],
                    organ_source=cl["organ_source"],
                    clearance_rate_ml_min=cl["clearance_rate_ml_min"],
                    extraction_ratio=cl["extraction_ratio"],
                    fraction_metabolized=cl["fraction_metabolized"],
                )
                self.session.add(cl_record)

        await self.session.commit()
        return await self.get_study(study_id)  # type: ignore

    async def get_study(self, study_id: uuid.UUID) -> Optional[DBWholeBodyPBPKStudy]:
        """Retrieve a PBPK study by ID."""
        stmt = (
            select(DBWholeBodyPBPKStudy)
            .where(DBWholeBodyPBPKStudy.id == study_id)
            .options(
                selectinload(DBWholeBodyPBPKStudy.organ_compartments),
                selectinload(DBWholeBodyPBPKStudy.clearance_rates),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[DBWholeBodyPBPKStudy]:
        """List PBPK studies with pagination."""
        stmt = (
            select(DBWholeBodyPBPKStudy)
            .order_by(DBWholeBodyPBPKStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
            .options(
                selectinload(DBWholeBodyPBPKStudy.organ_compartments),
                selectinload(DBWholeBodyPBPKStudy.clearance_rates),
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete_study(self, study_id: uuid.UUID) -> bool:
        """Delete a study by ID."""
        study = await self.get_study(study_id)
        if not study:
            return False
        await self.session.delete(study)
        await self.session.commit()
        return True
