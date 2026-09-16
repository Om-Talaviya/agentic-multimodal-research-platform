"""
FastAPI router for Bioprocess Bioreactor Digital Twin (Phase 62).
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db_session
from database.repositories.bioprocess_digital_twin_repo import BioprocessDigitalTwinRepository
from research.bioprocess.bioprocess_engine import BioprocessDigitalTwinEngine

router = APIRouter(prefix="/bioprocess", tags=["Bioprocess Digital Twin"])


class CreateRunRequest(BaseModel):
    run_name: str = Field(default="Bioreactor-mAb-Batch-2026-09")
    cell_line: str = Field(default="CHO-K1 (mAb Producer)")
    bioreactor_type: str = Field(default="Fed-Batch Stirred Tank")
    working_volume_liters: float = Field(default=50.0)


@router.post("/runs", status_code=status.HTTP_201_CREATED)
async def create_bioreactor_run(
    request: CreateRunRequest,
    db: AsyncSession = Depends(get_db_session),
):
    """Executes bioprocess digital twin simulation with kinetic ODE solver and MPC control policy."""
    repo = BioprocessDigitalTwinRepository(db)
    run = await repo.create_run(
        run_name=request.run_name,
        cell_line=request.cell_line,
        bioreactor_type=request.bioreactor_type,
        working_volume_liters=request.working_volume_liters,
    )

    sim_result = BioprocessDigitalTwinEngine.simulate_fed_batch_cycle(
        run_name=request.run_name,
        cell_line=request.cell_line,
        volume_l=request.working_volume_liters,
    )

    return await repo.add_telemetry_and_actions(
        run_id=run.id,
        telemetry_data=sim_result["telemetry"],
        actions_data=sim_result["actions"],
        final_titer=sim_result["final_titer"],
        final_viability=sim_result["final_viability"],
    )


@router.get("/runs")
async def list_bioreactor_runs(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session),
):
    """Lists bioreactor digital twin runs."""
    repo = BioprocessDigitalTwinRepository(db)
    return await repo.list_runs(limit=limit)


@router.get("/runs/{run_id}")
async def get_bioreactor_run(
    run_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Retrieves full bioreactor telemetry history and MPC control actions."""
    repo = BioprocessDigitalTwinRepository(db)
    run = await repo.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Bioreactor run not found")
    return run
