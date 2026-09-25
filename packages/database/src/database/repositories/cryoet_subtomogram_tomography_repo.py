"""Repository for Cryo-ET Subtomogram Averaging."""

import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from database.connection import AsyncSession
from database.models.cryoet_subtomogram_tomography import (
    DBCryoETTomogramStudy,
    DBCryoETSubtomogramParticle,
    DBCryoETResolutionClass,
)


class CryoETTomogramRepository:
    """Repository handling CRUD operations for Cryo-ET Subtomogram Averaging."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_study(
        self,
        study_name: str,
        cellular_context: str = "Intact Neuronal Synapse (In-Situ)",
        target_complex_name: str = "AMPAR-TARP Ion Channel Complex",
        particles_picked_count: int = 4,
        final_fsc_resolution_angstrom: float = 3.42,
        angular_search_step_deg: float = 3.75,
        summary_metrics: Optional[Dict[str, Any]] = None,
        particles: Optional[List[Dict[str, Any]]] = None,
        classes: Optional[List[Dict[str, Any]]] = None,
    ) -> DBCryoETTomogramStudy:
        study_id = uuid.uuid4()
        study = DBCryoETTomogramStudy(
            id=study_id,
            study_name=study_name,
            cellular_context=cellular_context,
            target_complex_name=target_complex_name,
            particles_picked_count=particles_picked_count,
            final_fsc_resolution_angstrom=final_fsc_resolution_angstrom,
            angular_search_step_deg=angular_search_step_deg,
            summary_metrics=summary_metrics or {},
        )
        self.session.add(study)
        await self.session.flush()

        if particles:
            for p in particles:
                part_row = DBCryoETSubtomogramParticle(
                    id=uuid.uuid4(),
                    study_id=study_id,
                    particle_id_str=p["particle_id_str"],
                    x_vox=p["x_vox"],
                    y_vox=p["y_vox"],
                    z_vox=p["z_vox"],
                    euler_rot_deg=p["euler_rot_deg"],
                    euler_tilt_deg=p["euler_tilt_deg"],
                    euler_psi_deg=p["euler_psi_deg"],
                    cross_correlation_score=p["cross_correlation_score"],
                    conformational_state=p.get("conformational_state", "Resting Closed"),
                )
                self.session.add(part_row)

        if classes:
            for c in classes:
                class_row = DBCryoETResolutionClass(
                    id=uuid.uuid4(),
                    study_id=study_id,
                    class_number=c["class_number"],
                    class_name=c["class_name"],
                    particle_occupancy_pct=c["particle_occupancy_pct"],
                    resolution_angstrom=c["resolution_angstrom"],
                    fsc_cutoff_type=c.get("fsc_cutoff_type", "FSC_0.143_GoldStandard"),
                )
                self.session.add(class_row)

        await self.session.commit()
        return await self.get_study(study_id)  # type: ignore

    async def get_study(self, study_id: uuid.UUID) -> Optional[DBCryoETTomogramStudy]:
        stmt = (
            select(DBCryoETTomogramStudy)
            .where(DBCryoETTomogramStudy.id == study_id)
            .options(
                selectinload(DBCryoETTomogramStudy.particles),
                selectinload(DBCryoETTomogramStudy.classes),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[DBCryoETTomogramStudy]:
        stmt = (
            select(DBCryoETTomogramStudy)
            .order_by(DBCryoETTomogramStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
            .options(
                selectinload(DBCryoETTomogramStudy.particles),
                selectinload(DBCryoETTomogramStudy.classes),
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
