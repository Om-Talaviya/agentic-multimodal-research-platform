"""
FastAPI router for Global Clinical Trial Logistics (Phase 63).
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db_session
from database.repositories.clinical_logistics_repo import ClinicalTrialLogisticsRepository
from research.logistics.clinical_logistics_engine import ClinicalTrialLogisticsEngine

router = APIRouter(prefix="/clinical-logistics", tags=["Clinical Trial Logistics"])


class CreateTrialNetworkRequest(BaseModel):
    trial_protocol_number: str = Field(default="PROTO-IMM-2026-03")
    trial_title: str = Field(default="Global Phase III mRNA Neoantigen Combination Trial")
    phase: str = Field(default="Phase III")
    product_storage_regime: str = Field(default="Ultra-Cold Chain (-80°C)")


@router.post("/trials", status_code=status.HTTP_201_CREATED)
async def create_trial_logistics_network(
    request: CreateTrialNetworkRequest,
    db: AsyncSession = Depends(get_db_session),
):
    """Executes global clinical trial logistics forecasting and cold-chain risk simulation."""
    repo = ClinicalTrialLogisticsRepository(db)
    net = await repo.create_network(
        trial_protocol_number=request.trial_protocol_number,
        trial_title=request.trial_title,
        phase=request.phase,
        product_storage_regime=request.product_storage_regime,
    )

    sim_result = ClinicalTrialLogisticsEngine.simulate_trial_logistics(
        protocol_no=request.trial_protocol_number,
        storage_regime=request.product_storage_regime,
    )

    return await repo.add_sites_and_routes(
        network_id=net.id,
        sites_data=sim_result["sites"],
        routes_data=sim_result["routes"],
        global_risk=sim_result["global_risk"],
    )


@router.get("/trials")
async def list_trial_networks(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session),
):
    """Lists global clinical trial logistics networks."""
    repo = ClinicalTrialLogisticsRepository(db)
    return await repo.list_networks(limit=limit)


@router.get("/trials/{trial_id}")
async def get_trial_network(
    trial_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Retrieves full clinical trial network with all site inventory gauges and cold-chain lanes."""
    repo = ClinicalTrialLogisticsRepository(db)
    net = await repo.get_network(trial_id)
    if not net:
        raise HTTPException(status_code=404, detail="Clinical trial network not found")
    return net
