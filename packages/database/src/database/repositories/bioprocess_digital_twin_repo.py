"""
Repository for Bioprocess Bioreactor Digital Twin (Phase 62).
"""
import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.bioprocess_digital_twin import (
    DBBioreactorRun,
    DBBioprocessTimeSeriesPoint,
    DBBioprocessControlAction,
)


class BioprocessDigitalTwinRepository:
    """Handles CRUD operations for bioreactor digital twin runs, telemetry, and control schedules."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_run(
        self,
        run_name: str,
        cell_line: str = "CHO-K1 (mAb Producer)",
        bioreactor_type: str = "Fed-Batch Stirred Tank",
        working_volume_liters: float = 50.0,
        metadata_info: Optional[Dict[str, Any]] = None,
    ) -> DBBioreactorRun:
        run = DBBioreactorRun(
            id=str(uuid.uuid4()),
            run_name=run_name,
            cell_line=cell_line,
            bioreactor_type=bioreactor_type,
            working_volume_liters=working_volume_liters,
            metadata_info=metadata_info or {},
        )
        self.session.add(run)
        await self.session.flush()
        await self.session.commit()
        return run

    async def add_telemetry_and_actions(
        self,
        run_id: str,
        telemetry_data: List[Dict[str, Any]],
        actions_data: List[Dict[str, Any]],
        final_titer: float = 4.8,
        final_viability: float = 92.5,
    ) -> DBBioreactorRun:
        for t in telemetry_data:
            pt = DBBioprocessTimeSeriesPoint(
                id=str(uuid.uuid4()),
                run_id=run_id,
                time_hours=t["time_hours"],
                viable_cell_density_10e6_ml=t["viable_cell_density_10e6_ml"],
                cell_viability_pct=t["cell_viability_pct"],
                glucose_concentration_g_l=t["glucose_concentration_g_l"],
                lactate_concentration_g_l=t["lactate_concentration_g_l"],
                dissolved_oxygen_pct=t.get("dissolved_oxygen_pct", 40.0),
                ph_level=t.get("ph_level", 7.10),
                product_titer_g_l=t["product_titer_g_l"],
            )
            self.session.add(pt)

        for a in actions_data:
            act = DBBioprocessControlAction(
                id=str(uuid.uuid4()),
                run_id=run_id,
                time_hours=a["time_hours"],
                feed_rate_ml_h=a["feed_rate_ml_h"],
                agitation_rpm=a.get("agitation_rpm", 180.0),
                sparge_o2_l_min=a.get("sparge_o2_l_min", 0.5),
                temperature_c=a.get("temperature_c", 36.8),
                policy_action_name=a.get("policy_action_name", "Glucose Bolus Feed"),
            )
            self.session.add(act)

        await self.session.flush()

        run = await self.get_run(run_id)
        if run:
            run.final_titer_g_l = final_titer
            run.final_viability_pct = final_viability
            self.session.add(run)

        await self.session.commit()
        return run

    async def get_run(self, run_id: str) -> Optional[DBBioreactorRun]:
        self.session.expire_all()
        query = (
            select(DBBioreactorRun)
            .options(
                selectinload(DBBioreactorRun.telemetry_points),
                selectinload(DBBioreactorRun.control_actions),
            )
            .where(DBBioreactorRun.id == run_id)
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def list_runs(self, limit: int = 50) -> List[DBBioreactorRun]:
        query = (
            select(DBBioreactorRun)
            .options(selectinload(DBBioreactorRun.telemetry_points))
            .order_by(desc(DBBioreactorRun.created_at))
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
