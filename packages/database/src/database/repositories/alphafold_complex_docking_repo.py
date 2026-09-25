"""Repository for AlphaFold Multimeric Complex & Co-Evolutionary Contact Model."""

import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from database.connection import AsyncSession
from database.models.alphafold_complex_docking import (
    DBAlphaFoldComplexStudy,
    DBInterfaceContactResidue,
    DBInterfaceEnergyMetric,
)


class AlphaFoldComplexRepository:
    """Repository handling CRUD operations for AlphaFold Complex Docking."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_study(
        self,
        study_name: str,
        target_complex_name: str = "PD-1 / PD-L1 Complex",
        chain_a_name: str = "PDCD1_HUMAN (Chain A)",
        chain_b_name: str = "CD274_HUMAN (Chain B)",
        mean_iptm_score: float = 0.88,
        mean_plddt_interface: float = 89.4,
        buried_surface_area_angstrom2: float = 1840.5,
        summary_metrics: Optional[Dict[str, Any]] = None,
        contacts: Optional[List[Dict[str, Any]]] = None,
        energy_metrics: Optional[List[Dict[str, Any]]] = None,
    ) -> DBAlphaFoldComplexStudy:
        study_id = uuid.uuid4()
        study = DBAlphaFoldComplexStudy(
            id=study_id,
            study_name=study_name,
            target_complex_name=target_complex_name,
            chain_a_name=chain_a_name,
            chain_b_name=chain_b_name,
            mean_iptm_score=mean_iptm_score,
            mean_plddt_interface=mean_plddt_interface,
            buried_surface_area_angstrom2=buried_surface_area_angstrom2,
            summary_metrics=summary_metrics or {},
        )
        self.session.add(study)
        await self.session.flush()

        if contacts:
            for c in contacts:
                contact_row = DBInterfaceContactResidue(
                    id=uuid.uuid4(),
                    study_id=study_id,
                    chain_a_residue=c["chain_a_residue"],
                    chain_b_residue=c["chain_b_residue"],
                    inter_residue_distance_angstrom=c["inter_residue_distance_angstrom"],
                    predicted_aligned_error_angstrom=c["predicted_aligned_error_angstrom"],
                    interaction_type=c.get("interaction_type", "hydrogen_bond"),
                    contact_plddt=c.get("contact_plddt", 90.0),
                )
                self.session.add(contact_row)

        if energy_metrics:
            for e in energy_metrics:
                energy_row = DBInterfaceEnergyMetric(
                    id=uuid.uuid4(),
                    study_id=study_id,
                    energy_component=e["energy_component"],
                    value_kcal_mol=e["value_kcal_mol"],
                    favorable_flag=e.get("favorable_flag", "FAVORABLE"),
                )
                self.session.add(energy_row)

        await self.session.commit()
        return await self.get_study(study_id)  # type: ignore

    async def get_study(self, study_id: uuid.UUID) -> Optional[DBAlphaFoldComplexStudy]:
        stmt = (
            select(DBAlphaFoldComplexStudy)
            .where(DBAlphaFoldComplexStudy.id == study_id)
            .options(
                selectinload(DBAlphaFoldComplexStudy.contacts),
                selectinload(DBAlphaFoldComplexStudy.energy_metrics),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[DBAlphaFoldComplexStudy]:
        stmt = (
            select(DBAlphaFoldComplexStudy)
            .order_by(DBAlphaFoldComplexStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
            .options(
                selectinload(DBAlphaFoldComplexStudy.contacts),
                selectinload(DBAlphaFoldComplexStudy.energy_metrics),
            )
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def delete_study(self, study_id: uuid.UUID) -> bool:
        study = await self.get_study(study_id)
        if not study:
            return False
        await self.session.delete(study)
        await self.session.commit()
        return True
